"""
logger.py — ლოგირების ერთიანი კონფიგურაცია მთელი backend-ისთვის.

იმპორტი main.py-ის თავში (side-effect-ისთვის) საკმარისია — ყველა
მოდულის logging.getLogger(...) ავტომატურად ამ ფორმატს გამოიყენებს.
"""

import logging
import sys


def setup_logging(level: int = logging.INFO) -> None:
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%H:%M:%S",
        stream=sys.stdout,
        force=True,  # თუ uvicorn-მაც უკვე დააკონფიგურირა logging, ჩვენი ფორმატი გაიმარჯვებს
    )


setup_logging()
