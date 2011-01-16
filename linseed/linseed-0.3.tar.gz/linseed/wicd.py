import dbus

def is_valid_network_id(network_type):
    try:
        id = network_type.GetCurrentNetworkID(0)
        return (id >= 0 and  id < network_type.GetNumberOfNetworks())
    except dbus.DBusException:
        # hopefully it's a UnknownMethodException
        return False

class WICD(object):
    def __init__(self):
        try:

            self.bus = dbus.SystemBus()

            self.wireless = dbus.Interface(
                self.bus.get_object('org.wicd.daemon', '/org/wicd/daemon/wireless'),
                'org.wicd.daemon.wireless')

            self.wired = dbus.Interface(
                self.bus.get_object('org.wicd.daemon', '/org/wicd/daemon/wired'),
                'org.wicd.daemon.wired')

        except dbus.DBusException as e:
            raise linseed.DataNotAvailable(str(e))
        
    is_wireless = property(lambda self: is_valid_network_id(self.wireless))
    is_wired = property(lambda self: is_valid_network_id(self.wired))

    essid = property(
        lambda self: self.wireless.GetWirelessProperty(
            self.wireless.GetCurrentNetworkID(0), 'essid'))
    quality = property(
        lambda self: self.wireless.GetWirelessProperty(
            self.wireless.GetCurrentNetworkID(0), 'quality'))
    
    def display(self):
        if self.is_wireless:
            return '{0} {1}%'.format(
                self.essid,
                self.quality)

        elif self.is_wired:
            return 'wired'

        else:
            return 'not connected'

    @staticmethod
    def name():
        return 'linseed_wicd'

    @staticmethod
    def description():
        return 'WICD connection status'
