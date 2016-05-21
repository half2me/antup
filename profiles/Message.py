class Message:
    """ANT+ Message"""

    def __init__(self, previous, raw):
        """
        :param previous: Previous message
        """
        self.previous = previous
        self.__raw = raw

    @property
    def raw(self):
        """ The raw message in byte array """
        return self.__raw
