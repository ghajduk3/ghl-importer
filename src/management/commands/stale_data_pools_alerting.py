import datetime
import logging
import typing

from django.conf import settings
from django.core import mail
from django.core.management.base import BaseCommand

from src import enums
from src import models

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = """
            Alerts if there are unprocessed stale data pools.
            ex. python manage.py process_data_pools 
            """

    log_prefix = "[UNPROCESS-DATA-POOLS]"

    def handle(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        logger.info(
            "{} Started command '{}'.".format(
                self.log_prefix,
                __name__.split(".")[-1],
            )
        )

        stale_unprocessed_pools = models.LoanPool.objects.filter(
            created_at__lte=datetime.datetime.now()
            - datetime.timedelta(hours=settings.STALE_LOAN_DATA_POOLS_TIME_DELTA),
            status=enums.LoanDataPoolStatus.UNPROCESSED.value,
        )
        if stale_unprocessed_pools:
            msg = "Found {} unprocessed stale loan data pools".format(stale_unprocessed_pools.count())
            logger.error("{} {}.".format(self.log_prefix, msg))
            mail.send_mail(
                from_email=settings.EMAIL_HOST_USER,
                subject="ERROR",
                message=msg,
                recipient_list=settings.LOGGING_EMAIL_RECIPIENT_LIST,
                fail_silently=False,
            )

        logger.info(
            "{} Finished command '{}'.".format(
                self.log_prefix,
                __name__.split(".")[-1],
            )
        )
