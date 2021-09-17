import logging
import logging.handlers


logger = logging.getLogger("ReferenceTester")
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")


def setUpLogger():
    """Sets up logger."""
    logger.setLevel(logging.DEBUG)
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(formatter)
    logger.addHandler(streamHandler)
