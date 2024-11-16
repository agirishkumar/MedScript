# from airflow.utils.log.logging_mixin import LoggingMixin

# class AirflowLogger(LoggingMixin):
#     def __new__(cls, *args, **kw):
#          if not hasattr(cls, '_instance'):
#              orig = super(AirflowLogger, cls)
#              cls._instance = orig.__new__(cls, *args, **kw)
#          return cls._instance
    
#     def __init__(self, name="airflow_task_logger"):
#         self.logger_name = name
#         super().__init__()

#     def log_info(self, msg):
#         self.log.info(f"{self.logger_name} - INFO - {msg}")

#     def log_warning(self, msg):
#         self.log.warning(f"{self.logger_name} - WARNING - {msg}")

#     def log_error(self, msg):
#         self.log.error(f"{self.logger_name} - ERROR - {msg}")

#     def log_debug(self, msg):
#         self.log.debug(f"{self.logger_name} - DEBUG - {msg}")

# logger = AirflowLogger()


import logging
logger = logging.getLogger(__name__)