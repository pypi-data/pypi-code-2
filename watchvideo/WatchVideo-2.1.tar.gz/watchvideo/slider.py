 #!/usr/bin/env python
# -*- coding: utf-8 -*- #

from watchvideo.qt.QtGui import (QSlider, QPainter, QStyleOptionProgressBar,
                                 QStyleOptionSlider, QStylePainter, QStyle,
                                 QMouseEvent)
from watchvideo.qt.QtCore import (QTimer, Qt)

class Slider(QSlider):
    def __init__(self, orientation, parent = None):
        QSlider.__init__(self, orientation, parent)
        self.setPageStep(1)
        self.paused = False
        self.setEnabled(False)
        self.max = 0
        self.value_when_pressed = 0
        self.progress_max = 0
        self.progress = 0
        self.setValue(0)
        self.last_value = 0
        self.lastSeeked = 0
        self.time_when_paused = 0
        self.is_sliderMoving = False
        self.MediaPlayer = None
        self.last_valid_value = 0
        self.progressBarHeight = 0

        self.timer_update_slider = QTimer()
        self.timer_update_slider.timeout.connect(self.update_slider)
        
        self.sliderPressed.connect(self.on_slider_press)
        self.sliderReleased.connect(self.on_slider_release)
        self.sliderMoved.connect(self.on_slider_move)
        
        self.setSetStyleSheet()
        
        
    def setSetStyleSheet(self):
        #Modified version of this one:
        #http://thesmithfam.org/blog/2010/03/10/fancy-qslider-stylesheet/
        if self.progressBarHeight == 0:
          height = 17
        else:
          height = self.progressBarHeight
        
        self.setStyleSheet('''\

                    QSlider::groove:horizontal {
                    border: 1px solid #bbb;
                    background: white;
                    height: %spx;
                    border-radius: 4px;
                    }

                    QSlider::sub-page:horizontal {
                    background: qlineargradient(x1: 0, y1: 0,    x2: 0, y2: 1,
                        stop: 0 #66e, stop: 1 #bbf);
                    background: qlineargradient(x1: 0, y1: 0.2, x2: 1, y2: 1,
                        stop: 0 #bbf, stop: 1 #55f);
                    border: 1px solid #777;
                    height: 10px;
                    border-radius: 4px;
                    }


                    QSlider::handle:horizontal {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #eee, stop:1 #ccc);
                    border: 1px solid #777;
                    width: 13px;
                    margin-top: -2px;
                    margin-bottom: -2px;
                    border-radius: 4px;
                    }

                    QSlider::handle:horizontal:hover {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #fff, stop:1 #ddd);
                    border: 1px solid #444;
                    border-radius: 4px;
                    }

                    QSlider::sub-page:horizontal:disabled {
                    background: #bbb;
                    border-color: #999;
                    }

                    QSlider::handle:horizontal:disabled {
                    background: #eee;
                    border: 1px solid #aaa;
                    border-radius: 4px;
                    }

        ''' % height)
        
    def add_player(self, player):
        self.MediaPlayer = player

    def start(self):
        self.paused = False
    
    def pause(self):
        self.paused = not self.paused
        self.time_when_paused = self.MediaPlayer.get_position() * 1000
        
        
    def reset(self, progress_bar=True):
        if self.timer_update_slider.isActive():
            self.timer_update_slider.stop()
        self.setValue(0)
        self.last_valid_value = self.last_value = self.lastSeeked = 0
        if progress_bar:
            self.progress = self.progress_max = 0
        self.update()
        
    def complete(self):
        self.reset(progress_bar=False)
        
    def loadfile(self, filepath, position=0.0):
        self.setEnabled(True)
        self.paused = False
        self.filepath = filepath
        self.MediaPlayer.set_position( position )
        self.time_when_paused = self.last_valid_value = self.last_value = 0
        if not self.timer_update_slider.isActive():
            self.timer_update_slider.start(1000)
    
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            newEvent = QMouseEvent( event.type(), event.pos(), event.globalPos(),
                Qt.MouseButton( event.button() ^ Qt.LeftButton ^ Qt.MidButton ),
                Qt.MouseButtons( event.buttons() ^ Qt.LeftButton ^ Qt.MidButton ),
                event.modifiers() )
            QSlider.mousePressEvent(self, newEvent )
        else:
            QSlider.mousePressEvent(self, event )

        
    def seekTick(self):
        if self.value() != self.lastSeeked:
            lastSeeked = self.value()
            f_pos = (float)(self.lastSeeked)/1000.0
            self.emit (sliderDragged( f_pos ))

    
    def on_slider_press(self):
        self.value_when_pressed = self.value()
    
    def on_slider_move(self):
        self.is_sliderMoving = True
    
    
    def on_slider_release(self):
        if self.value() < self.max:
            self.last_valid_value = self.last_value
            self.MediaPlayer.set_position( self.value() / 1000.0)
        elif self.is_sliderMoving:
            self.setValue(self.value_when_pressed)
        else:
            self.setValue(self.last_value)
            
        self.is_sliderMoving = False
    
    def update_slider(self):
        if self.paused: 
            #keep updating the progress bar
            self.update()
            return
        
        if self.MediaPlayer.get_position() is not None:
            self.setValue(self.MediaPlayer.get_position() * 1000)
            self.last_value = self.MediaPlayer.get_position() * 1000
            
            
    def paintEvent(self, ev):
        p = QPainter (self)
        opt = QStyleOptionSlider()
        self.initStyleOption(opt)
        opt2 = QStyleOptionProgressBar()
        opt2.initFrom(self)
        if self.progress_max > 0:
            opt2.maximum = self.progress_max
            opt2.progress = self.progress
        else:
            opt2.maximum = -1
            opt2.progress = -1
        
        if self.progressBarHeight == 0:
          self.progressBarHeight = opt2.rect.height() - 3
          self.setSetStyleSheet()
        
        sp = QStylePainter(self)
        sp.drawControl(QStyle.CE_ProgressBar, opt2)
        
        opt.subControls = QStyle.SC_SliderHandle
        self.style().drawComplexControl(QStyle.CC_Slider, opt, p, self)
