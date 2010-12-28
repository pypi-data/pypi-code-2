
def migrate(self, xmlFilePath, typeToCreate, folder):
    from v2.theme.migrator import XMLMigrator
    
    #Create the migrator
    migrator = XMLMigrator(self, xmlFilePath, typeToCreate, folder)
    
    #Finally migrate
    print("=== Starting Migration. ===")
    migrator.startMigration()
    return "=== Migration sucessfull. Created %d items on folder %s (%d errors and %d skipped) ==="%(migrator.created, migrator.folderPath, migrator.errors, migrator.skipped)

