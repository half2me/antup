from profiles.wrapper import Message, lazyproperty


class PowerMessage(Message):
    """ Message from Power Meter """

    @lazyproperty
    def dataPageNumber(self):
        """
        :return: Data Page Number (int)
        """
        return self.raw[1]

    @lazyproperty
    def eventCount(self):
        """
        The update event count field is incremented each time the information in the message is updated.
        There are no invalid values for update event count.
        The update event count in this message refers to updates of the standard Power-Only main data page (0x10)
        :return: Power Event Count
        """
        return self.raw[2]

    @lazyproperty
    def instantaneousCadence(self):
        """
        The instantaneous cadence field is used to transmit the pedaling cadence recorded from the power sensor.
        This field is an instantaneous value only; it does not accumulate between messages.
        :return: Instantaneous Cadence (W)
        """
        return self.raw[4]

    @lazyproperty
    def accumulatedPower(self):
        """
        Accumulated power is the running sum of the instantaneous power data and is incremented at each update
        of the update event count. The accumulated power field rolls over at 65.535kW.
        :return:
        """
        return (self.__raw[6] << 8) | self.__raw[5]

    @lazyproperty
    def instantaneousPower(self):
        """ Instantaneous power (W) """
        return (self.__raw[8] << 8) | self.__raw[7]

    @lazyproperty
    def averagePower(self):
        """
        Under normal conditions with complete RF reception, average power equals instantaneous power.
        In conditions where packets are lost, average power accurately calculates power over the interval
        between the received messages
        :return: Average power (Watts)
        """
        return (self.accumulatedPower - self.previous.accumulatedPower) / (self.eventCount - self.previous.eventCount)
