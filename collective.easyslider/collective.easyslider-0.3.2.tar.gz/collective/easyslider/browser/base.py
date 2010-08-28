

class AbstractSliderView(object):
    """
    must have settings attribute specified
    """
    
    def css(self):
        return """
#slider-container{
    width: %(width)ipx;
    height: %(height)ipx;
    margin: %(centered)s;
}
#slider, #slider li{ 
    width:%(width)ipx;
    height:%(height)ipx;
}
#nextBtn{ 
    left:%(width)ipx;
    top:-%(next_top)ipx
}
#prevBtn{
	top:-%(prev_top)ipx;
}	
    """ % {
                'width' : self.settings.width,
                'height' : self.settings.height,
                'next_top' : ((self.settings.height/2) + 75) + 50,
                'prev_top' : ((self.settings.height/2) + 50),
                'centered' : self.settings.centered and 'auto' or '0'
            }
        
    def js(self):
        return """
jQuery(document).ready(function(){	
	jQuery("#slider").easySlider({
	    speed : %(speed)i,
	    vertical: %(vertical)s,
	    auto : %(auto)s,
	    pause : %(pause)i,
	    continuous : %(continuous)s,
	    navigation_type: '%(navigation_type)s',
	    effect: '%(effect)s',
	    fadeNavigation: %(fade_navigation)s
	});
});
        """ % {
            'speed' : self.settings.speed,
            'vertical' : str(self.settings.vertical).lower(),
            'auto' : str(self.settings.auto).lower(),
            'pause' : self.settings.pause,
            'continuous' : str(self.settings.continuous).lower(),
            'navigation_type' : self.settings.navigation_type,
            'effect' : self.settings.effect,
            'fade_navigation' : str(self.settings.fade_navigation).lower()
        }