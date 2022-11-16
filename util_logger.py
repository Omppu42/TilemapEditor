import os
from datetime import datetime


class Logger:
    def __init__(self):
        self.logs_folder = "Logs\\"
        if not os.path.isdir(self.logs_folder):
            os.mkdir(self.logs_folder)

        self.log_file = "latest.log"
        self.reset_logs_file()


    def reset_logs_file(self):
        with open(self.logs_folder+self.log_file, "w"):
            pass

    def debug(self, msg: str):
        self.log_to_file("DEBUG", msg)

    def log(self, msg: str):
        self.log_to_file("INFO", msg)

    def warning(self, msg: str):
        self.log_to_file("WARNING", msg)

    def error(self, msg: str):
        self.log_to_file("ERROR", msg)
    
    def critical(self, msg: str):
        self.log_to_file("CRITICAL", msg)


    def log_to_file(self, level: str, msg: str):
        now = datetime.now()
        now = now.strftime("%H:%M:%S")

        with open(self.logs_folder+self.log_file, "a") as f:
            f.write(f"{now} - [{level}] {msg}\n")

logger = Logger()