import logging
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    logger.error(
        f"Unhandled exception in {context['view'].__class__.__name__}",
        exc_info=True  # 👈 logs the cause + stack trace
    )
    return exception_handler(exc, context)