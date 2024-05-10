import logging

# Set up a logger with timestamp + message format
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create a formatter
formatter = logging.Formatter('%(asctime)s - %(message)s')

# Create a handler, set its level and formatter
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(handler)

