import cy_kit
from cyx.loggers import LoggerService
svc = cy_kit.singleton(LoggerService)
svc.info("test")