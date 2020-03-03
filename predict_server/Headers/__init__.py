import logging
import os

logger = logging.getLogger("server")


def not_test(selffunc):
    if "TEST" in os.environ and os.environ["TEST"] == "Handler":
        logger.info("Skip function in test")
        return False
    else:
        selffunc()


def test(selffunc):
    if "TEST" in os.environ and os.environ["TEST"] == "Handler":
        selffunc()
