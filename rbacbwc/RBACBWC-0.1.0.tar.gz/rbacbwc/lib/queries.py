import sqlalchemy as sa
import sqlalchemy.sql as sasql

from compstack.sqlalchemy import db

def assignment_permission_join(obj_asmnt_tname, obj_cname, ref_cname,
        perm_asmnt_tname, perms_cname, approved_val, qry_alias,
        group_user_link=False, gu_asmnt_tname='', users_cname=''):
    """
        joins an assignment table with a permission assignment table

        Example: Join the users<->bundles table to denied bundle permissions.
        The resulting recordset looks like:

        perm_id, user_id, approved_sum

        where the first two columns contain obvious values and the last column
        indicates the number of times the permission has been denied for that
        permission & user by a group or NULL if it has never been denied.

        example:
            obj_asmnt_tname = 'bundle_user_assignments'
            obj_cname = 'bundle_id'
            ref_cname = 'user_id'

            perm_asmnt_tname = 'bundle_permission_assignments'
            perms_cname = 'permission_id'

            approved_val = -1
            qry_alias = 'ubd'

        group_user_link: if set to True, object is bundles and reference is
        groups and an additional join is requested linking the group to a user
        so that the result set has user_id column (or equivalent).  Example for
        groups<->bundles with group_user_link = True:

            perm_id, group_id, user_id, approved_sum

    """
    # object<->ref table & columns
    oa_tbl = db.meta.tables[obj_asmnt_tname]
    oa_obj_col = oa_tbl.c[obj_cname]
    oa_ref_col = oa_tbl.c[ref_cname]

    # object<->perms table & columns
    pa_tbl = db.meta.tables[perm_asmnt_tname]
    pa_obj_col = pa_tbl.c[obj_cname]
    pa_perm_col = pa_tbl.c[perms_cname]

    # build query
    qry = sasql.select(
        [
            pa_perm_col,
            oa_ref_col,
            sa.func.sum(pa_tbl.c.approved).label(u'approved_sum')
        ], from_obj =
            pa_tbl.outerjoin(
                oa_tbl,
                oa_obj_col == pa_obj_col
            )
    ).where(
        pa_tbl.c.approved == approved_val
    ).group_by(
        pa_perm_col,
        oa_ref_col
    )

    if group_user_link:
        qry = qry.alias('inner_%s' % qry_alias)

        gua_tbl = db.meta.tables[gu_asmnt_tname]

        gul_qry = sasql.select(
            [
                qry.c[perms_cname],
                qry.c[ref_cname],
                gua_tbl.c[users_cname],
                qry.c.approved_sum
            ], from_obj =
            qry.outerjoin(
                gua_tbl,
                gua_tbl.c[ref_cname] == qry.c[ref_cname]
            )
        )
        qry = gul_qry.alias(qry_alias)
    else:
        qry = qry.alias(qry_alias)

    return qry
