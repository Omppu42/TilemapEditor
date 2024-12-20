import os, sys
from datetime import datetime

from settings import settings


class Logger:
    def __init__(self, log_level: int=0):
        if not os.path.isdir(settings.LOGS_FOLDER):
            os.mkdir(settings.LOGS_FOLDER)

        self.log_file = "\\latest.log"
        self.reset_logs_file()

        self.logging_level = log_level
        # 0 : debug ->
        # 1 : info ->
        # ...
        # 4 : fatal

        assert(self.logging_level <= 4 and self.logging_level >= 0), f"Logging level must be 0, 1, 2, 3 or 4. Currently it's {self.logging_level}"


    def reset_logs_file(self):
        with open(settings.LOGS_FOLDER+self.log_file, "w"):
            pass

    def debug(self, msg: str):
        if self.logging_level > 0: return
        self.log_to_file("DEBUG", msg)

    def log(self, msg: str):
        if self.logging_level > 1: return
        self.log_to_file("INFO", msg)

    def warning(self, msg: str):
        if self.logging_level > 2: return
        self.log_to_file("WARNING", msg)
        print("Warning logged:", msg)

    def error(self, msg: str):
        if self.logging_level > 3: return
        self.log_to_file("ERROR", msg)
        print("Error logged:", msg)
    
    def fatal(self, msg: str):
        self.log_to_file("FATAL", msg)
        print("FATAL, QUITTING:", msg)
        sys.exit()


    def log_to_file(self, level: str, msg: str):
        now = datetime.now()
        now = now.strftime("%H:%M:%S")

        with open(settings.LOGS_FOLDER+self.log_file, "a") as f:
            f.write(f"{now} - [{level}] {msg}\n")

logger = Logger(log_level=0)