from profiles.Message import Message
from wrapper import lazyproperty


class SpeedCadenceMessage(Message):
    """ Message from Speed & Cadence sensor """

    maxCadenceEventTime = 65536
    maxSpeedEventTime = 65536
    maxSpeedRevCount = 65536
    maxCadenceRevCount = 65536

    @lazyproperty
    def cadenceEventTime(self):
        """ Represents the time of the last valid bike cadence event (1/1024 sec) """
        return (self.raw[2] << 8) | self.raw[1]

    @lazyproperty
    def cumulativeCadenceRevolutionCount(self):
        """ Represents the total number of pedal revolutions """
        return (self.raw[4] << 8) | self.raw[3]

    @lazyproperty
    def speedEventTime(self):
        """ Represents the time of the last valid bike speed event (1/1024 sec) """
        return (self.raw[6] << 8) | self.raw[5]

    @lazyproperty
    def cumulativeSpeedRevolutionCount(self):
        """ Represents the total number of wheel revolutions """
        return (self.raw[8] << 8) | self.raw[7]

    @lazyproperty
    def speedEventTimeDiff(self):
        if self.previous is None:
            return None
        elif self.speedEventTime < self.previous.speedEventTime:
            # Rollover
            return (self.speedEventTime - self.previous.speedEventTime) + self.maxSpeedEventTime
        else:
            return self.speedEventTime - self.previous.speedEventTime

    @lazyproperty
    def cadenceEventTimeDiff(self):
        if self.previous is None:
            return None
        elif self.cadenceEventTime < self.previous.cadenceEventTime:
            # Rollover
            return (self.cadenceEventTime - self.previous.cadenceEventTime) + self.maxCadenceEventTime
        else:
            return self.cadenceEventTime - self.previous.cadenceEventTime

    @lazyproperty
    def speedRevCountDiff(self):
        if self.previous is None:
            return None
        elif self.cumulativeSpeedRevolutionCount < self.previous.cumulativeSpeedRevolutionCount:
            # Rollover
            return (
                       self.cumulativeSpeedRevolutionCount - self.previous.cumulativeSpeedRevolutionCount) + self.maxSpeedRevCount
        else:
            return self.cumulativeSpeedRevolutionCount - self.previous.cumulativeSpeedRevolutionCount

    @lazyproperty
    def cadenceRevCountDiff(self):
        if self.previous is None:
            return None
        elif self.cumulativeCadenceRevolutionCount < self.previous.cumulativeCadenceRevolutionCount:
            # Rollover
            return (
                       self.cumulativeCadenceRevolutionCount - self.previous.cumulativeCadenceRevolutionCount) + self.maxCadenceRevCount
        else:
            return self.cumulativeCadenceRevolutionCount - self.previous.cumulativeCadenceRevolutionCount

    def speed(self, c):
        """
        :param c: circumference of the wheel (mm)
        :return: The current speed (m/sec)
        """
        if self.previous is None:
            return 0
        if self.speedEventTime == self.previous.speedEventTime:
            return self.previous.speed(c)
        return self.speedRevCountDiff * 1.024 * c / self.speedEventTimeDiff

    @lazyproperty
    def cadence(self):
        """
        :return: RPM
        """
        if self.previous is None:
            return 0
        if self.cadenceEventTime == self.previous.cadenceEventTime:
            return self.previous.cadence
        return self.cadenceRevCountDiff * 1024 * 60 / self.cadenceEventTimeDiff
