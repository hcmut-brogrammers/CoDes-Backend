import logging
import sys
import typing as t
import fastapi as p
from functools import lru_cache

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.INFO)
stdout_formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
stdout_handler.setFormatter(stdout_formatter)
logger.addHandler(stdout_handler)


@lru_cache
def create_logger() -> logging.Logger:
    return logger


LoggerDep = t.Annotated[logging.Logger, p.Depends(create_logger)]
