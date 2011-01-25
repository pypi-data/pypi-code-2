drop_attribute('CWUser', 'working_branch')
add_relation_definition('CWUser', 'might_edit', 'VersionedFile')
rql('SET U might_edit X WHERE E might_edit X, E user U')
drop_entity_type('Editor')
