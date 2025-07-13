import logging

from template_fastapi.settings.logging import get_logger

# For backward compatibility with the original tests
# We still need to support the original behavior
logger = get_logger(__name__)


def hello_world(verbose: bool = False):
    """Simple hello world function with optional verbose logging."""
    if verbose:
        # Configure basic logging for verbose mode (for backward compatibility)
        logging.basicConfig(level=logging.DEBUG)
    # Use module-level logging for test compatibility
    logging.debug("Hello World")


if __name__ == "__main__":
    hello_world(verbose=True)
