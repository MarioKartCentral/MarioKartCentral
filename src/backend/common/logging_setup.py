import logging
import sys

# Set up root logger to print to stdout, similar to print()
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s: %(message)s',
    stream=sys.stdout
)

def setup_logging():
    # This can be called at app startup to ensure logging is configured
    pass
