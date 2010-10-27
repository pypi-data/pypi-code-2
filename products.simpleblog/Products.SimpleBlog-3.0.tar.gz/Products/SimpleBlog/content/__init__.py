# This statement makes Blog, BlogEntry and BlogFolder available to import via:
#   from Products.SimpleBlog.content import Blog, BlogFolder, BlogEntry
# Without it, you would have to use:
#   from Products.SimpleBlog.content.Blog import Blog
#   from Products.SimpleBlog.content.BlogFolder import BlogFolder
#   from Products.SimpleBlog.content.BlogEntry import BlogEntry

from blog import Blog
from blogfolder import BlogFolder
from blogentry import BlogEntry
