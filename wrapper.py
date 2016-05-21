def lazyproperty(fn):
    attr_name = '__' + fn.__name__

    @property
    def _lazyprop(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, fn(self))
        return getattr(self, attr_name)

    return _lazyprop


class CandyWrapper:
    """Wrapper for the ANT+ Communication and Devices"""

    def __init__(self):
        self.devices = []

    def listAvailableDevices(self):
        """List all ANT+ capable hardwear"""
        return None

    def loadAllAvailableDevices(self):
        """Loads all available ANT+ hardwear devices"""
        return self.devices

    def loadFirstAvailableDevice(self):
        """Loads the first available ANT+ hardwear device"""
        return self.devices[0]


class Device:
    """Wrapper for ANT+ capable hardware"""

    def __init__(self):
        self.node = Node()


class Node:
    """ANT+ Node"""

    def scan(self):
        return None

    def getFreeChannel(self):
        return Channel()


class Channel:
    """ANT+ Channel"""