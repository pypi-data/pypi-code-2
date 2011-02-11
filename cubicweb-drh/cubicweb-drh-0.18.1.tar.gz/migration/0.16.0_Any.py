# add topic relation
add_relation_definition('EmailThread','topic','Application')
sync_schema_props_perms()

# set topics
rql('SET T topic A WHERE E in_thread T, E sender EA, P primary_email EA, A for_person P')
rql('SET T topic A WHERE E in_thread T, E recipients EA, P primary_email EA, A for_person P, NOT T topic A')
