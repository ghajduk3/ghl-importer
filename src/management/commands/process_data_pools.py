import logging
import typing

from django.core.management.base import BaseCommand

from common import utils as common_utils
from src.services import loan_data_pool as data_pool_services

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = """
            Processes loan data received in the pool.
            ex. python manage.py process_data_pools 
            """

    log_prefix = "[PROCESS-DATA-POOLS]"

    def handle(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        logger.info(
            "{} Started command '{}'.".format(
                self.log_prefix,
                __name__.split(".")[-1],
            )
        )

        try:
            data_pool_services.process_data_pools()
        except Exception as e:
            logger.exception(
                "{} Unexpected exception occurred while processing data pools. Error: {}.".format(
                    self.log_prefix,
                    common_utils.get_exception_message(exception=e),
                )
            )

        logger.info(
            "{} Finished command '{}'.".format(
                self.log_prefix,
                __name__.split(".")[-1],
            )
        )
