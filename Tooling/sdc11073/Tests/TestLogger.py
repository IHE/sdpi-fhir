import logging
import logging.handlers

logger = logging.getLogger("ReferenceTester")
_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

def setUpLogger():
    """Sets up DiscoveryProxy logger."""
    logger.setLevel(logging.DEBUG)
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(_formatter)
    logger.addHandler(streamHandler)
