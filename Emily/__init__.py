import logging
logger = logging.getLogger(__name__)
import coloredlogs
coloredlogs.ColoredStreamHandler.default_severity_to_style['INFO'] = {'underline': True}
coloredlogs.ColoredStreamHandler.default_severity_to_style['WARNING'] = {'inverse': True}

coloredlogs.install(level=logging.DEBUG)
