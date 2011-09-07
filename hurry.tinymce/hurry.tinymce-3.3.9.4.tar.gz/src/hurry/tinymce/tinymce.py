from hurry.resource import Library, ResourceInclusion

tinymce_lib = Library('tinymce')

tinymce = ResourceInclusion(tinymce_lib, 'tiny_mce_src.js',
                            minified='tiny_mce.js')

