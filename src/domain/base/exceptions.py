class BaseMsgException(Exception):
    """Bass class for msg exceptions."""

    message: str

    def __str__(self):
        return self.message
