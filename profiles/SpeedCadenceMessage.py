from __future__ import print_function

from profiles.wrapper import Message


def lazyproperty(fn):
    attr_name = '__' + fn.__name__

    @property
    def _lazyprop(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, fn(self))
        return getattr(self, attr_name)

    return _lazyprop


class SpeedCadenceMessage(Message):
    """ Message from Speed & Cadence sensor """

    def __init__(self, previous, raw):
        Message.__init__(self, previous)
        self.__raw = raw

    @property
    def raw(self):
        """ The raw message in byte array """
        return self.__raw

    @lazyproperty
    def cadenceEventTime(self):
        """ Represents the time of the last valid bike cadence event (1/1024 sec) """
        return (self.__raw[2] << 8) | self.__raw[1]

    @lazyproperty
    def cumulativeCadenceRevolutionCount(self):
        """ Represents the total number of pedal revolutions """
        return (self.__raw[4] << 8) | self.__raw[3]

    @lazyproperty
    def speedEventTime(self):
        """ Represents the time of the last valid bike speed event (1/1024 sec) """
        return (self.__raw[6] << 8) | self.__raw[5]

    @lazyproperty
    def cumulativeSpeedRevolutionCount(self):
        """ Represents the total number of wheel revolutions """
        return (self.__raw[8] << 8) | self.__raw[7]

    def speed(self, c):
        """
        :param c: circumference of the wheel (mm)
        :return: The current speed (m/sec)
        """
        if self.previous is None:
            return 0
        return (self.cumulativeSpeedRevolutionCount - self.previous.cumulativeSpeedRevolutionCount) * 1.024 * c / (
            self.speedEventTime - self.previous.speedEventTime)
