from blazeutils.helpers import tolist
from blazeutils.strings import case_cw2us
import sqlalchemy as sa
import sqlalchemy.orm as saorm
import sqlalchemy.sql as sasql
from sqlalchemy.util import classproperty

from compstack.rbac.lib.queries import assignment_permission_join
from compstack.sqlalchemy import db
from compstack.sqlalchemy.lib.declarative import DefaultMixin

def create_permission_mixin(pe_class_name, pe_tbl_pk_col, pe_ref_col_name,
            belongs_to_backref='permissions', users_cname='user_id', groups_cname='group_id',
            bundles_cname='bundle_id', perms_cname='permission_id',
            bundle_pk_attr='id', tbl_prefix=''):

    user_pa_tname = tbl_prefix + 'user_permission_assignments'
    group_pa_tname = tbl_prefix + 'group_permission_assignments'
    bundle_pa_tname = tbl_prefix + 'bundle_permission_assignments'

    def assigned_objs_helper(assignments_tbl_name, obj_cname, permid):
        astbl = db.meta.tables[assignments_tbl_name]
        objid_col = astbl.c[obj_cname]
        permid_col = astbl.c[perms_cname]

        s = sasql.select(
            [objid_col],
            sasql.and_(permid_col == permid, astbl.c.approved == 1)
            )
        approved = [r[0] for r in db.sess.execute(s)]
        s = sasql.select(
            [objid_col],
            sasql.and_(permid_col == permid, astbl.c.approved == -1)
            )
        denied = [r[0] for r in db.sess.execute(s)]
        return approved, denied

    def replace_objs_helper(assignments_tbl_name, obj_cname, permid, approved_ids, denied_ids):
        astbl = db.meta.tables[assignments_tbl_name]
        permid_col = astbl.c[perms_cname]

        insval = []

        approved_ids = tolist(approved_ids)
        denied_ids = tolist(denied_ids)

        # delete existing permission assignments for this user (i.e. we start over)
        db.sess.execute(astbl.delete(permid_col == permid))

        # insert "approved" records
        if approved_ids:
            insval.extend([{perms_cname : permid, obj_cname : oid, 'approved' : 1} for oid in approved_ids])

        # insert "denied" records
        if denied_ids:
            insval.extend([{perms_cname : permid, obj_cname : oid, 'approved' : -1} for oid in denied_ids])

        # do inserts
        if insval:
            db.sess.execute(astbl.insert(), insval)

    class PermissionMixin(DefaultMixin):

        name = sa.Column(sa.Unicode(250), nullable=False)

        ###
        ### Constraints
        ###
        @classproperty
        def __table_args__(cls):
            return (sa.UniqueConstraint(pe_ref_col_name, 'name'), {})

        ###
        ### Relationships
        ###
        @classproperty
        def belongs_to(cls):
            br = saorm.backref(belongs_to_backref, passive_deletes=True)
            return saorm.relation(pe_class_name, backref=br)

        @classmethod
        def replace_users(cls, permid, approved_ids=None, denied_ids=None):
            return replace_objs_helper(user_pa_tname, users_cname, permid, approved_ids, denied_ids)

        @classmethod
        def assigned_users(cls, permid):
            return assigned_objs_helper(user_pa_tname, users_cname, permid)

        @classmethod
        def replace_groups(cls, permid, approved_ids=None, denied_ids=None):
            return replace_objs_helper(group_pa_tname, groups_cname, permid, approved_ids, denied_ids)

        @classmethod
        def assigned_groups(cls, permid):
            return assigned_objs_helper(group_pa_tname, groups_cname, permid)

        @classmethod
        def replace_bundles(cls, permid, approved_ids=None, denied_ids=None):
            return replace_objs_helper(bundle_pa_tname, bundles_cname, permid, approved_ids, denied_ids)

        @classmethod
        def assigned_bundles(cls, permid):
            return assigned_objs_helper(bundle_pa_tname, bundles_cname, permid)

    # set an attribute on the class that will create the FK column that references
    # the protected entity's records
    def cp_func(cls):
        return sa.Column(sa.Integer, sa.ForeignKey(pe_tbl_pk_col), nullable=False)
    setattr(PermissionMixin, pe_ref_col_name, classproperty(cp_func))

    return PermissionMixin

def _create_has_permissions_mixin(assignments_tbl_name, col1_name, col2_name):

    class HasPermsMixin(DefaultMixin):

        @classmethod
        def perm_assignments_tbl(cls):
            return db.meta.tables[assignments_tbl_name]

        @classmethod
        def replace_permissions(cls, targetid, approved_perm_ids, denied_perm_ids):
            user_pk_col = cls.perm_assignments_tbl().c[col1_name]

            insval = []

            # delete existing permission assignments for this user (i.e. we start over)
            db.sess.execute(cls.perm_assignments_tbl().delete(user_pk_col == targetid))

            # insert "approved" records
            if approved_perm_ids is not None and len(approved_perm_ids) != 0:
                insval.extend([{col1_name : targetid, col2_name : pid, 'approved' : 1} for pid in approved_perm_ids])

            # insert "denied" records
            if denied_perm_ids is not None and len(denied_perm_ids) != 0:
                insval.extend([{col1_name : targetid, col2_name : pid, 'approved' : -1} for pid in denied_perm_ids])

            # do inserts
            if insval:
                db.sess.execute(cls.perm_assignments_tbl().insert(), insval)

        @classmethod
        def assigned_permissions(cls, targetid):
            user_pk_col = cls.perm_assignments_tbl().c[col1_name]
            perm_pk_col = cls.perm_assignments_tbl().c[col2_name]

            s = sasql.select(
                [perm_pk_col],
                sasql.and_(user_pk_col == targetid, cls.perm_assignments_tbl().c.approved == 1)
                )
            approved = [r[0] for r in db.sess.execute(s)]
            s = sasql.select(
                [perm_pk_col],
                sasql.and_(user_pk_col == targetid, cls.perm_assignments_tbl().c.approved == -1)
                )
            denied = [r[0] for r in db.sess.execute(s)]

            return approved, denied
    return HasPermsMixin

def _create_assignable_mixin(tbl_name, my_col_name, refs_col_name, refs_type):

    class AssignableMixin(object):
        pass

    def replace_refs(cls, targetid, replace_ids):
        m2m_tbl = db.meta.tables[tbl_name]
        m2m_my_col = m2m_tbl.c[my_col_name]

        insval = []

        # delete existing assignments
        db.sess.execute(m2m_tbl.delete(m2m_my_col == targetid))

        # insert new assignments
        insval = [{my_col_name : targetid, refs_col_name : rid} for rid in replace_ids]

        # do inserts
        if insval:
            db.sess.execute(m2m_tbl.insert(), insval)
        return len(insval)
    setattr(AssignableMixin, 'replace_' + refs_type, classmethod(replace_refs))

    def count_refs(cls, targetid=None):
        m2m_tbl = db.meta.tables[tbl_name]
        m2m_my_col = m2m_tbl.c[my_col_name]

        sql = sasql.select([sa.func.count(m2m_my_col)], from_obj=[m2m_tbl])
        if targetid:
            sql = sql.where(m2m_my_col == targetid)
        return db.sess.execute(sql).scalar()
    setattr(AssignableMixin, 'count_' + refs_type, classmethod(count_refs))

    def assigned_refs(cls, targetid):
        m2m_tbl = db.meta.tables[tbl_name]
        m2m_my_col = m2m_tbl.c[my_col_name]
        m2m_refs_col = m2m_tbl.c[refs_col_name]

        sql = sasql.select([m2m_refs_col], from_obj=[m2m_tbl]).where(m2m_my_col == targetid)
        res = db.sess.execute(sql)
        assigned_ids = [row[m2m_refs_col] for row in res]

        return assigned_ids
    setattr(AssignableMixin, 'assigned_' + refs_type, classmethod(assigned_refs))

    return AssignableMixin

def create_user_mixin(users_cname='user_id', groups_cname='group_id',
            bundles_cname='bundle_id', perms_cname='permission_id',
            perms_tname='permissions', perms_pe_cname='application_id',
            tbl_prefix=''):

    perms_tname = tbl_prefix + perms_tname
    bundle_users_tname = tbl_prefix + 'bundle_user_assignments'
    bundle_perms_tname = tbl_prefix + 'bundle_permission_assignments'
    group_users_tname = tbl_prefix + 'group_user_assignments'
    group_perms_tname = tbl_prefix + 'group_permission_assignments'
    bundle_groups_tname = tbl_prefix + 'bundle_group_assignments'
    group_users_tname = tbl_prefix + 'group_user_assignments'

    HasPermsMixin = _create_has_permissions_mixin(
        tbl_prefix + 'user_permission_assignments',
        users_cname,
        perms_cname
    )
    HasGroupsMixin = _create_assignable_mixin(
        group_users_tname,
        users_cname,
        groups_cname,
        'groups'
    )
    HasBundlesMixin = _create_assignable_mixin(
        bundle_users_tname,
        users_cname,
        bundles_cname,
        'bundles'
    )

    class UserMixin(HasPermsMixin, HasGroupsMixin, HasBundlesMixin):

        @classmethod
        def has_permissions(cls, userid, protected_entity_id, pnames):
            # user-permissions table and columns
            up_tbl = cls.perm_assignments_tbl()
            up_user_col = up_tbl.c[users_cname]
            up_perm_col = up_tbl.c[perms_cname]

            # permissions table
            perms_tbl = db.meta.tables[perms_tname]

            # denied user-bundle permissions
            ubd_qry = assignment_permission_join(
                bundle_users_tname, bundles_cname, users_cname, bundle_perms_tname,
                perms_cname, -1, 'ubd'
            )
            # approved user-bundle permissions
            uba_qry = assignment_permission_join(
                bundle_users_tname, bundles_cname, users_cname, bundle_perms_tname,
                perms_cname, 1, 'uba'
            )
            # denied user-group permissions
            ugd_qry = assignment_permission_join(
                group_users_tname, groups_cname, users_cname, group_perms_tname,
                perms_cname, -1, 'ugd'
            )
            # approved user-group permissions
            uga_qry = assignment_permission_join(
                group_users_tname, groups_cname, users_cname, group_perms_tname,
                perms_cname, 1, 'uga'
            )
            # denied group-bundle permissions
            gbd_qry = assignment_permission_join(
                bundle_groups_tname, bundles_cname, groups_cname, bundle_perms_tname,
                perms_cname, -1, 'gbd', True, group_users_tname, users_cname
            )
            # approved group-bundle permissions
            gba_qry = assignment_permission_join(
                bundle_groups_tname, bundles_cname, groups_cname, bundle_perms_tname,
                perms_cname, 1, 'gba', True, group_users_tname, users_cname
            )

            # main select
            sql = sasql.select(
                [
                    perms_tbl.c.name,
                    up_tbl.c.approved,
                    sa.func.coalesce(ubd_qry.c.approved_sum, 0).label('ubd_approved_sum'),
                    sa.func.coalesce(uba_qry.c.approved_sum, 0).label('uba_approved_sum'),
                    sa.func.coalesce(ugd_qry.c.approved_sum, 0).label('ugd_approved_sum'),
                    sa.func.coalesce(uga_qry.c.approved_sum, 0).label('uga_approved_sum'),
                    sa.func.coalesce(gbd_qry.c.approved_sum, 0).label('gbd_approved_sum'),
                    sa.func.coalesce(gba_qry.c.approved_sum, 0).label('gba_approved_sum'),
                ], from_obj=
                perms_tbl.outerjoin(
                    up_tbl,
                    sasql.and_(
                        up_perm_col == perms_tbl.c.id,
                        up_user_col == userid,
                    )
                ).outerjoin(
                    ubd_qry,
                    sasql.and_(
                        ubd_qry.c[perms_cname] == perms_tbl.c.id,
                        ubd_qry.c[users_cname] == userid
                    )
                ).outerjoin(
                    uba_qry,
                    sasql.and_(
                        uba_qry.c[perms_cname] == perms_tbl.c.id,
                        uba_qry.c[users_cname] == userid
                    )
                ).outerjoin(
                    ugd_qry,
                    sasql.and_(
                        ugd_qry.c[perms_cname] == perms_tbl.c.id,
                        ugd_qry.c[users_cname] == userid
                    )
                ).outerjoin(
                    uga_qry,
                    sasql.and_(
                        uga_qry.c[perms_cname] == perms_tbl.c.id,
                        uga_qry.c[users_cname] == userid
                    )
                ).outerjoin(
                    gba_qry,
                    sasql.and_(
                        gba_qry.c[perms_cname] == perms_tbl.c.id,
                        gba_qry.c[users_cname] == userid
                    )
                ).outerjoin(
                    gbd_qry,
                    sasql.and_(
                        gbd_qry.c[perms_cname] == perms_tbl.c.id,
                        gbd_qry.c[users_cname] == userid
                    )
                )
            ).where(
                sasql.and_(
                    perms_tbl.c.name.in_(pnames),
                    perms_tbl.c[perms_pe_cname] == protected_entity_id
                )
            )

            rows = db.sess.execute(sql)

            # create a dictionary with the permission
            # names as a key and None for the value
            retval = dict([(k, None) for k in pnames])

            # loop through the rows returned and set the resulting permission
            # as applicable
            for row in rows:
                ubd_val = row['ubd_approved_sum']
                uba_val = row['uba_approved_sum']
                ugd_val = row['ugd_approved_sum']
                uga_val = row['uga_approved_sum']
                gbd_val = row['gbd_approved_sum']
                gba_val = row['gba_approved_sum']
                if row[up_tbl.c.approved] == -1 or ubd_val < 0:
                    approved = False
                elif row[up_tbl.c.approved] == 1 or uba_val > 0:
                    approved = True
                elif ugd_val < 0 or gbd_val < 0:
                    approved = False
                elif uga_val > 0 or gba_val > 0:
                    approved = True
                else:
                    approved = False
                retval[row[perms_tbl.c.name]] = approved
            return retval


    return UserMixin

def create_group_mixin(users_cname='user_id', groups_cname='group_id',
            bundles_cname='bundle_id', perms_cname='permission_id',
            group_pk_attr='id', tbl_prefix=''):

    HasPermsMixin = _create_has_permissions_mixin(
        tbl_prefix + 'group_permission_assignments',
        groups_cname,
        perms_cname
    )
    HasUsersMixin = _create_assignable_mixin(
        tbl_prefix + 'group_user_assignments',
        groups_cname,
        users_cname,
        'users'
    )
    HasBundlesMixin = _create_assignable_mixin(
        tbl_prefix + 'bundle_group_assignments',
        groups_cname,
        bundles_cname,
        'bundles'
    )
    class GroupMixin(HasPermsMixin, HasUsersMixin, HasBundlesMixin):
        pass
    return GroupMixin

def create_bundle_mixin(users_cname='user_id', groups_cname='group_id',
            bundles_cname='bundle_id', perms_cname='permission_id',
            bundle_pk_attr='id', tbl_prefix=''):
    HasPermsMixin = _create_has_permissions_mixin(
        tbl_prefix + 'bundle_permission_assignments',
        bundles_cname,
        perms_cname
    )
    HasUsersMixin = _create_assignable_mixin(
        tbl_prefix + 'bundle_user_assignments',
        bundles_cname,
        users_cname,
        'users'
    )
    HasGroupsMixin = _create_assignable_mixin(
        tbl_prefix + 'bundle_group_assignments',
        bundles_cname,
        groups_cname,
        'groups'
    )
    class BundleMixin(HasPermsMixin, HasUsersMixin, HasGroupsMixin):
        pass
    return BundleMixin

def _create_permission_assignment_table(name, col1_name, col1_refs, col2_name, col2_refs):
    tbl = \
        sa.Table(name, db.meta,
            sa.Column('id', sa.Integer, primary_key = True),
            sa.Column(col1_name, sa.Integer, sa.ForeignKey(col1_refs, ondelete='cascade'), nullable = False),
            sa.Column(col2_name, sa.Integer, sa.ForeignKey(col2_refs, ondelete='cascade'), nullable = False),
            sa.Column('approved', sa.Integer, sa.CheckConstraint('approved in (-1, 1)'), nullable = False)
        )
    idx = sa.Index('ix_%s_unique' % name,
            tbl.c[col1_name],
            tbl.c[col2_name],
            unique=True
        )
    return tbl, idx

def _create_m2m_table(name, col1_name, col1_refs, col2_name, col2_refs):
    tbl = sa.Table(name, db.meta,
        sa.Column(col1_name, sa.Integer, sa.ForeignKey(col1_refs, ondelete='cascade'), nullable = False),
        sa.Column(col2_name, sa.Integer, sa.ForeignKey(col2_refs, ondelete='cascade'), nullable = False),
    )
    idx = sa.Index('ix_%s_unique' % name,
            tbl.c[col1_name],
            tbl.c[col2_name],
            unique=True
        )
    return tbl, idx

def create_schema_objects(users_col='user_id', users_col_refs='users.id',
        perms_col='permission_id', perms_col_refs='permissions.id',
        groups_col='group_id', groups_col_refs='groups.id',
        bundles_col='bundle_id', bundles_col_refs='bundles.id', tbl_prefix=''):

    # user <--> perm assignments
    tbl_upa, idx_upa = _create_permission_assignment_table(
        tbl_prefix + 'user_permission_assignments',
        users_col,
        "%s%s" % (tbl_prefix, users_col_refs),
        perms_col,
        "%s%s" % (tbl_prefix, perms_col_refs),
    )
    # group <--> perm assignments
    tbl_gpa, idx_gpa = _create_permission_assignment_table(
        tbl_prefix + 'group_permission_assignments',
        groups_col,
        "%s%s" % (tbl_prefix, groups_col_refs),
        perms_col,
        "%s%s" % (tbl_prefix, perms_col_refs),
    )
    # bundle <--> perm assignments
    tbl_bpa, idx_bpa = _create_permission_assignment_table(
        tbl_prefix + 'bundle_permission_assignments',
        bundles_col,
        "%s%s" % (tbl_prefix, bundles_col_refs),
        perms_col,
        "%s%s" % (tbl_prefix, perms_col_refs),
    )
    # group <--> user assignments
    tbl_gua, idx_gua = _create_m2m_table(
        tbl_prefix + 'group_user_assignments',
        users_col,
        "%s%s" % (tbl_prefix, users_col_refs),
        groups_col,
        "%s%s" % (tbl_prefix, groups_col_refs),
    )
    # bundle <--> user assignments
    tbl_bua, idx_bua = _create_m2m_table(
        tbl_prefix + 'bundle_user_assignments',
        users_col,
        "%s%s" % (tbl_prefix, users_col_refs),
        bundles_col,
        "%s%s" % (tbl_prefix, bundles_col_refs),
    )
    # bundle <--> group assignments
    tbl_bga, idx_bga = _create_m2m_table(
        tbl_prefix + 'bundle_group_assignments',
        bundles_col,
        "%s%s" % (tbl_prefix, bundles_col_refs),
        groups_col,
        "%s%s" % (tbl_prefix, groups_col_refs),
    )
    return tbl_upa, idx_upa, tbl_gpa, idx_gpa, tbl_gua, idx_gua, tbl_bpa, idx_bpa, tbl_bua, idx_bua, tbl_bga, idx_bga
