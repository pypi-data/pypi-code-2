## Script (Python) "docrop"
##title=do the actual crop
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=values=None

request = container.REQUEST
RESPONSE =  request.RESPONSE

field = context.getField('image')

field.editCrop(context,
               request.crop,
               request.x1,
               request.y1,
               request.x2,
               request.y2,
               scale = request.cropScale
               )

dest = request.get('last_referer', context.absolute_url())
RESPONSE.redirect(dest)
