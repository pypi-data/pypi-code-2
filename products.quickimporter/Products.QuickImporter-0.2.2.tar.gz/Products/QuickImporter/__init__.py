import QuickImporter

def initialize( context ):
	context.registerClass(
		meta_type = 'Quick Importer',
		permission = QuickImporter.myPermission,
		constructors = (
			QuickImporter.addForm,
			QuickImporter.manage_doQuickImport),
	)
