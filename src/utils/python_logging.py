import logging


def setup_logging():
    logger = logging.getLogger("app")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if logger.handlers:
        return logger

    log_formatter = logging.Formatter(
        '%(asctime)s %(levelname)s %(filename)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    logger.addHandler(console_handler)

    try:
        file_handler = logging.FileHandler('app.log', encoding='utf-8', mode='a')
        file_handler.setFormatter(log_formatter)
        logger.addHandler(file_handler)
    except (OSError, PermissionError):
        # Fall back to console-only logging when the log directory is not writable.
        pass

    return logger