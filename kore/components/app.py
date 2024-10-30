import json
import logging
import os
import time
from datetime import datetime

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QApplication

APP_CONFIG_PATH = "./src/config/app.json"
LOGGING_PATH = "./logs"


class App(QApplication):
    """custom application,"""

    config: dict
    debug: bool

    name:str
    version:str
    
    set_style = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        
        self.start_time: float = time.perf_counter()

        self.set_style.connect(self._set_stylesheet)

        self._load_config()
        self._config_logging()


        self.log.debug(f"{self.app_data["name"]} v{self.app_data["version"]} started in DEBUG mode !")

    def run(self) -> None:
        """run the application loop, with a catch for event loop runtime errors."""
        
        try:
            startup_time = int((time.perf_counter() - self.start_time) * 1000)
            self.log.debug(f"Startup time: {startup_time}ms")
            self.exec()
        
        except Exception as exc:
            self._report_crash(exc)

    def _report_crash(self, exception: Exception):
        print(f"EXCEPTION CATCH: {exception}")

    def _load_config(self) -> None:
        """load application configuration from the config/app.json file and store it"""
        with open(APP_CONFIG_PATH, "r") as config_file:
            self.app_data = json.load(config_file)
            
        self.name = self.app_data["name"]
        self.version = self.app_data["version"]

    def _set_stylesheet(self, sheet:str):
        self.setStyleSheet(sheet)

    def _config_logging(self) -> None:
        """Configure logging with custom colors for console and efficient file output."""
        log_fmt = "{levelname} [{asctime} ({name})]: {message}"
        date_fmt = "%Y/%m/%d %H:%M:%S"

        color_codes = {
            "DEBUG": "\033[34m",  # Blue
            "INFO": "\033[32m",  # Green
            "WARNING": "\033[33m",  # Yellow
            "ERROR": "\033[31m",  # Red
            "CRITICAL": "\033[31;1m",  # Bold Red
        }

        class ColorFormatter(logging.Formatter):
            def format(self, record: logging.LogRecord) -> str:
                levelname = record.levelname
                color = color_codes.get(levelname, "")
                reset = "\033[0m"
                record.levelname = f"{color}{levelname[0]}{reset}{color}"
                result = super().format(record)
                record.levelname = levelname  # Reset levelname
                return f"{result}{reset}"

        # Create console handler with color formatting
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(
            ColorFormatter(fmt=log_fmt, datefmt=date_fmt, style="{")
        )

        """
        if UNIQUE_LOGS:
            log_name = "lastet.log"
        else:
        """

        log_name = f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"

        # check logging path
        log_dir = LOGGING_PATH
        os.makedirs(log_dir, exist_ok=True)

        # Create file handler
        file_handler = logging.FileHandler(os.path.join(log_dir, log_name), mode="w")
        file_handler.setFormatter(
            logging.Formatter(fmt=log_fmt, datefmt=date_fmt, style="{")
        )

        debug = self.app_data["environment"]["debug_mode"]
        logging_level = logging.DEBUG if debug else logging.INFO

        # Configure root logger
        self.log = logging.getLogger()
        self.log.setLevel(logging_level)  # Set the desired log level
        self.log.addHandler(console_handler)
        self.log.addHandler(file_handler)
