# ===============================================================
# Project: VAMBEX — Volatility Adjusted Momentum Bands EXtended
# Author: Andre Pinheiro
# Date: 2025.12.17
# Version: v1.0.0
# Description: Central logging configuration for the VAMBEX system.
# ===============================================================

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging(
    level: int = logging.INFO,
    log_dir: str = "logs",
    log_file: str = "vambex.log",
) -> None:
    """
    Configure application-wide logging using the ROOT logger.

    All modules should use:
        logger = logging.getLogger(__name__)
    """

    # ---- Create log directory ----
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    log_file_path = log_path / log_file

    # ---- Root logger ----
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Avoid duplicate handlers
    if root_logger.handlers:
        return

    formatter = logging.Formatter(
        "[VAMBEX] %(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # ---- Console handler ----
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # ---- Rotating file handler ----
    file_handler = RotatingFileHandler(
        filename=log_file_path,
        maxBytes=5_000_000,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
