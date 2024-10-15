import logging
 
class Applicationlog:
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        if not self.logger.hasHandlers():
            file_handler = logging.FileHandler("application.log", mode="a", encoding="utf-8")
            console_handler = logging.StreamHandler()
    
            formatter = logging.Formatter("%(asctime)s | %(levelname)s | GBB | %(message)s")
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
    
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
 
    def loggings(self, level, email, file_name, func_name, msg):
        log_message = f"{email} | workflowbuilder | {file_name} | {func_name} | {msg}"
        getattr(self.logger, level.lower(), self.logger.info)(log_message)