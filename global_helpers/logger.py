import logging
import os

# Set up a logger with timestamp + message format
logger = logging.getLogger(__name__)

# Create a handler
handler = logging.StreamHandler()

# Create a formatter with time, parent directory + file name, and message
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(parentdir)s/%(filename)s - %(message)s')

# Set a filter to add parentdir attribute to log records
class ParentDirFilter(logging.Filter):
    def filter(self, record):
        record.parentdir = os.path.basename(os.path.dirname(record.pathname))
        return True

handler.addFilter(ParentDirFilter())
handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(handler)