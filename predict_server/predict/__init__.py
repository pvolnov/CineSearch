import logging
import os

logger = logging.getLogger("predicting")


def not_test(selffunc):
    if "TEST" in os.environ and os.environ["TEST"] == "Predict":
        logger.info("Skip function in test")
        return False
    else:
        selffunc()


def test(selffunc):
    if "TEST" in os.environ and os.environ["TEST"] == "Predict":
        selffunc()
