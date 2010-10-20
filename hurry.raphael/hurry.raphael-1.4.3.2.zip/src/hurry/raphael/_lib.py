from hurry.resource import Library, ResourceInclusion

raphael = Library('raphael', 'raphael-build')

raphael = ResourceInclusion(raphael, 'raphael.js', minified='raphael-min.js')