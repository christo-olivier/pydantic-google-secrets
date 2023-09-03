import logging
import os
from config import Settings


logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))

settings = Settings()

print(f"my_secret_value: `{settings.my_secret_value}`")
