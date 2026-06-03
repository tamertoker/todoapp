"""Uygulama günlüğü (logging) kurulumu.

Hem konsola hem de veri dizinindeki bir dosyaya yazar; böylece bir sorun
olduğunda ne olduğunu sonradan görebiliriz.
"""

from __future__ import annotations

import logging
from pathlib import Path


def setup_logging(level: int = logging.INFO, log_file: Path | None = None) -> None:
    handlers: list[logging.Handler] = [logging.StreamHandler()]
    if log_file is not None:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file, encoding="utf-8"))

    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)-7s %(name)s — %(message)s",
        handlers=handlers,
    )
