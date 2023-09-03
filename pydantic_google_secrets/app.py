import logging
import os
from config import Settings


logging.basicConfig(level=os.getenv("log_level", "INFO"))

settings = Settings()

print(f"my_secret_value: `{settings.my_secret_value}`")
