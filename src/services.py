import logging
import typing

from src import enums
from src import models

logger = logging.getLogger(__name__)

_LOG_PREFIX = "[GHL-SERVICE]"


def save_loan_data_to_pool(raw_payload: typing.Dict) -> None:
    logger.info(
        "{} Saving raw payload to the pool for processing (raw_data={}).".format(
            _LOG_PREFIX, raw_payload
        )
    )
    pool_data = models.LoanPool.objects.create(
        loan_id=None,
        status=enums.LoanDataPoolStatus.IN_PROCESS.value,
        status_name=enums.LoanDataPoolStatus.IN_PROCESS.name,
        payload=raw_payload,
    )
    logger.info(
        "{} Saved raw payload to the pool (pool_id={}).".format(
            _LOG_PREFIX, pool_data.id
        )
    )
