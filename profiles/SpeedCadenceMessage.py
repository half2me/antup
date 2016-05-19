from profiles.wrapper import Message, lazyproperty


class SpeedCadenceMessage(Message):
    """ Message from Speed & Cadence sensor """

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

    def cadence(self):
        """
        :return: RPM
        """
        if self.previous is None:
            return 0
        return (self.cumulativeCadenceRevolutionCount - self.previous.cumulativeCadenceRevolutionCount) * 1024 * 60 / (
            self.cadenceEventTime - self.previous.cadenceEventTime)