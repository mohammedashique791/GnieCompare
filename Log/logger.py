import logging
 
class MeteringLog:
    def __init__(self):
        self.logger = logging.getLogger("MeteringLogger")
        self.logger.setLevel(logging.INFO)
        if not self.logger.hasHandlers():
            handler = logging.FileHandler("metering_log.log")
            handler.setFormatter(logging.Formatter('%(asctime)s :- %(levelname)s | %(message)s'))
            self.logger.addHandler(handler)
 
    def log_performance(self, email, system, filename, function_name, start_time, end_time, duration_ms):
        self.logger.info(
            f"GBB {email} | {system} | {filename} | {function_name} | Start Time: {start_time:.4f} | End Time: {end_time:.4f} | Duration: {duration_ms:.4f} s"
        )
