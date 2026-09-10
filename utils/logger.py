import logging
import os
from pathlib import Path


def get_logger(name: str = "railway"):

    log_directory = Path("logs")
    log_directory.mkdir(exist_ok=True)

    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )

    file_handler = logging.FileHandler(
        log_directory / "railway.log",
        encoding="utf-8"
    )

    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    # Show logs in the console when running the application.
    # Avoid console logging during pytest because pytest
    # temporarily captures and closes the console stream.
    if "PYTEST_CURRENT_TEST" not in os.environ:

        console_handler = logging.StreamHandler()

        console_handler.setFormatter(
            formatter
        )

        logger.addHandler(
            console_handler
        )

    return logger