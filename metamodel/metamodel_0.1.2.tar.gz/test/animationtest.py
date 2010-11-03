from metamodel import SubscribableModel, Property
from metamodel.animation import ClockModel, AnimationManager, AnimationChannel, IntAnimationKey
if __name__ == "__main__":
    class TestModel(SubscribableModel):
        prop1 = Property(int, 10)

    clock = ClockModel()
    a = TestModel()
    manager = AnimationManager(clock=clock)
    chan = AnimationChannel(model=a, prop="prop1", loop=True, interpolation="linear")
    chan.addChild(IntAnimationKey(time=0, value=0))
    chan.addChild(IntAnimationKey(time=10, value=10.0))
    lastkey = IntAnimationKey(time=20, value=5.0)
    chan.addChild(lastkey)
    manager.addChild(chan)
    # t = 0.0
    clock.time = 0.0
    assert(a.prop1 == 0.0)
    # t = 5.0
    clock.time = 5.0
    assert(a.prop1 == 5.0)
    # t = 10.0
    clock.time = 10.0
    assert(a.prop1 == 10.0)
    # t = 15.0
    clock.time = 15.0
    assert(a.prop1 == 7.5)
    # t = 20.0
    clock.time = 20.0
    assert(a.prop1 == 5.0)
    # t = 30.0
    clock.time = 30.0
    assert(a.prop1 == 10.0)
    # t = 2015.0
    clock.time = 2015.0
    assert(a.prop1 == 7.5)
    # key value change
    lastkey.value = 20.0
    assert(a.prop1 == 15.0)
    # key time change
    lastkey.time = 4020.0
    assert(a.prop1 == 15.0)

