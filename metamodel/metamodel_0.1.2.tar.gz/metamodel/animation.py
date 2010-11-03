"""
Animation system for models.
"""

from basemodel import SubscribableModel
from properties import Property, SingleChoice, Vector2, PropertyFrom
from math import sin, pi
from cubicspline import cubicspline
from numpy import array

def linear(val):
    """
    Linear interpolation
    """
    return val

def sinus(val):
    """
    Sinusoidal interpolation (goes from 0 to 1 following the curve of a sinus)
    """
    val = (val-0.5)*pi
    return (sin(val)+1.0)/2.0

INTERPOLATIONS = { "linear": linear,
         "sinus":  sinus   }

class ClockModel(SubscribableModel):
    time = Property(float, 0.0)

class AnimationManager(SubscribableModel):
    clock = Property(ClockModel)
    def __init__(self, *args, **kwargs):
        self._prevkeys = []
        self._prevvals = {}
        SubscribableModel.__init__(self, *args, **kwargs)

    def setProperty(self, name, value):
        SubscribableModel.setProperty(self, name, value)
        if name == "clock" and value:
            value.subscribe("time", self.time_changed)

    def check_ni_channel(self, chan, currtime):
        children = chan.getChildren()
        if chan.loop:
            duration = children[-1].time
            if currtime > duration:
                currtime = currtime - int(currtime/duration)*duration
        for idx, key in enumerate(children[:-1]):
            next = children[idx+1]
            if key.time <= currtime and next.time >= currtime:
                val = key.value
                if chan in self._prevvals and val == self._prevvals[chan]:
                    return
                self._prevvals[chan] = val
                setattr(chan.model, chan.prop, val)
                key.subscribe("time", self.key_changed)
                key.subscribe("value", self.value_changed)
                next.subscribe("time", self.key_changed)
                next.subscribe("value", self.value_changed)
                self._prevkeys.append(next)
                self._prevkeys.append(key)
                return

    def check_spline_channel(self, chan, currtime):
        children = chan.getChildren()
        if chan.loop:
            duration = children[-1].time
            if currtime > duration:
                currtime = currtime - int(currtime/duration)*duration
        splinedata = []
        childtimes = []
        for child in children:
            childtimes.append(child.time)
            splinedata.append([child.time+child.ctrl1[0], child.value+child.ctrl1[1]])
            splinedata.append([child.time, child.value])
            splinedata.append([child.time+child.ctrl2[0], child.value+child.ctrl2[1]])
        for idx, t in enumerate(childtimes[:-1]):
            next_t = childtimes[idx+1]
            if t <= currtime and currtime <= next_t:
                f = (currtime-t) / (next_t - t)
                data = splinedata[1+(idx*3):2+((idx+1)*3)]
                data = array(data)
                time,val = cubicspline(data, int(f*256))
                if chan in self._prevvals and val == self._prevvals[chan]:
                    return
                self._prevvals[chan] = val
                if chan.idx == -1:
                    setattr(chan.model, chan.prop, val)
                else:
                    obj_val = getattr(chan.model, chan.prop)
                    obj_val[int(chan.idx)] = val
                    setattr(chan.model, chan.prop, obj_val)
                key = children[idx]
                next = children[idx+1]
                key.subscribe("time", self.key_changed)
                key.subscribe("value", self.value_changed)
                next.subscribe("time", self.key_changed)
                next.subscribe("value", self.value_changed)
                self._prevkeys.append(next)
                self._prevkeys.append(key)
                return


    def check_channel(self, chan, currtime):
        children = chan.getChildren()
        intp_function = INTERPOLATIONS[chan.interpolation]
        if chan.loop:
            duration = children[-1].time
            if currtime > duration:
                currtime = currtime - int(currtime/duration)*duration
        for idx, key in enumerate(children[:-1]):
            next = children[idx+1]
            if key.time <= currtime and next.time >= currtime:
                f = (currtime-key.time) / (next.time - key.time)
                f = intp_function(f)
                val = key.value + (f*(next.value - key.value))
                if chan in self._prevvals and val == self._prevvals[chan]:
                    return
                self._prevvals[chan] = val
                if chan.idx == -1:
                    setattr(chan.model, chan.prop, val)
                else:
                    obj_val = getattr(chan.model, chan.prop)
                    obj_val[int(chan.idx)] = val
                    setattr(chan.model, chan.prop, obj_val)
                key.subscribe("time", self.key_changed)
                key.subscribe("value", self.value_changed)
                next.subscribe("time", self.key_changed)
                next.subscribe("value", self.value_changed)
                self._prevkeys.append(next)
                self._prevkeys.append(key)
                return

    def key_changed(self, val): 
        self.time_changed(self.clock.time)

    def value_changed(self, val):
        self.time_changed(self.clock.time)

    def time_changed(self, val):
        for prevkey in self._prevkeys:
            prevkey.unsubscribe("time", self.key_changed)
            prevkey.unsubscribe("value", self.value_changed)
        self._prevkeys = []
        for chan in self.getChildren():
            proptype = chan.model.trait(chan.prop)._proptype
            if proptype == str or issubclass(proptype, SubscribableModel):
                self.check_ni_channel(chan, val)
            else:
                if chan.interpolation in ["linear","sinus"]:
                    self.check_channel(chan, val)
                elif chan.interpolation == "spline":
                    print "spline interpolation"
                    self.check_spline_channel(chan, val)

class AnimationKey(SubscribableModel):
    time = Property(float, 0.0)

class IntAnimationKey(AnimationKey):
    value = Property(int, 0.0)
    ctrl1 = Vector2([1, 0])
    ctrl2 = Vector2([-1, 0])

class FloatAnimationKey(AnimationKey):
    value = Property(float, 0.0)
    ctrl1 = Vector2([-5, 0])
    ctrl2 = Vector2([5, 0])

class ModelAnimationKey(AnimationKey):
    value = Property(SubscribableModel)

class StringAnimationKey(AnimationKey):
    value = Property(str, "")

class AnimationChannel(SubscribableModel):
    name = Property(str,"animation channel")
    model = Property(SubscribableModel)
    prop = PropertyFrom("model")
    idx = Property(int,-1)
    loop = Property(bool, False)
    interpolation = SingleChoice(options=["linear","sinus","spline"], default="linear")
    builds = ["AnimationKey"]

    def addPoints(self, points):
        proptype = self.model.trait(self.prop)._proptype
        klass = None
        if proptype == str:
            klass = StringAnimationKey
        elif proptype == int:
            klass = IntAnimationKey
        elif proptype in [float, list]:
            klass = FloatAnimationKey
        elif issubclass(proptype, SubscribableModel):
            klass = ModelAnimationKey
        else:
            raise ValueError, "property type not supported "+str(proptype)
        for time, value in points:
            self.addChild(self.new(klass, time=time, value=value))


if __name__ == "__main__":
    class TestModel(SubscribableModel):
        prop1 = Property(int, 10)

    clock = ClockModel()
    a = TestModel()
    manager = AnimationManager(clock=clock)
    chan1 = AnimationChannel(model=a, prop="prop1", loop=True)
    chan1.addChild(IntAnimationKey(time=0, value=0))
    chan1.addChild(IntAnimationKey(time=10, value=10.0))
    lastkey = IntAnimationKey(time=20, value=5.0)
    chan1.addChild(lastkey)
    manager.addChild(chan1)
    # t = 0.0
    clock.time = 0.0
    assert(a.prop1 == 0.0)
    print a.prop1
    # t = 5.0
    clock.time = 5.0
    assert(a.prop1 == 5.0)
    print a.prop1
    # t = 10.0
    clock.time = 10.0
    assert(a.prop1 == 10.0)
    print a.prop1
    # t = 15.0
    clock.time = 15.0
    assert(a.prop1 == 7.5)
    print a.prop1
    # t = 20.0
    clock.time = 20.0
    assert(a.prop1 == 5.0)
    print a.prop1
    # t = 30.0
    clock.time = 30.0
    assert(a.prop1 == 10.0)
    print a.prop1
    # t = 2015.0
    clock.time = 2015.0
    assert(a.prop1 == 7.5)
    print a.prop1
    # key value change
    lastkey.value = 20.0
    assert(a.prop1 == 15.0)
    # key time change
    lastkey.time = 4020.0
    print a.prop1
    assert(a.prop1 == 15.0)

