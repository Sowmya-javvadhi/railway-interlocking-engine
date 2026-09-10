from pathlib import Path

from utils.logger import get_logger


def test_logger_creates_log_file():

    logger = get_logger("test_logger")

    logger.info("Test log message")

    log_file = Path("logs/railway.log")

    assert log_file.exists()

    content = log_file.read_text(
        encoding="utf-8"
    )

    assert "Test log message" in content