import sqlalchemy as sa

from compstack.rbac.lib import create_schema_objects

from rbacbwc_ta.model.entities import Permission

tbl_upa, idx_upa, tbl_gpa, idx_gpa, tbl_gua, idx_gua, tbl_bpa, idx_bpa, \
tbl_bua, idx_bua, tbl_bga, idx_bga = create_schema_objects()

idx_perms_cover = sa.Index(
    'ix_permissions_coverage',
    Permission.id,
    Permission.name,
    Permission.application_id
)

# auth_ prefixed objects
tbl_auth_upa, idx_auth_upa, tbl_auth_gpa, idx_auth_gpa, tbl_auth_gua, \
idx_auth_gua, tbl_auth_bpa, idx_auth_bpa, tbl_auth_bua, idx_auth_bua, \
tbl_auth_bga, idx_auth_bga = create_schema_objects(tbl_prefix='auth_')
