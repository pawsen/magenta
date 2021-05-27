#!/usr/bin/env python3

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


print("logger.exception\n")
try:
    out = 2/0
except ZeroDivisionError as e:
    logger.exception("Division by zero problem")
else:
    out = 2


print("\n\nlogger.error(exc_info=True)\n")
try:
    out = 2/0
except ZeroDivisionError as e:
    logger.error(f"Division by zero problem.", exc_info=True)
    print("\n")
    logger.error(f"Division by zero problem. {e}", exc_info=True)
else:
    out = 2
