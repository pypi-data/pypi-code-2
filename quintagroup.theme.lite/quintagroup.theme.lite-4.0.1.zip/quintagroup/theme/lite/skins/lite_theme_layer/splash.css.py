## Script (Python) "splash.css"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=p1, p2
##title=
##
#return ".section-front-page #region-content {background-image: url(getSplashImage/%d);}" % DateTime().millis()
return "#portal-top {background-image: url(%s);}" % context.getSplashImage()
