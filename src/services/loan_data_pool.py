import json
import logging
import typing

import simplejson

from common import utils as common_utils
from src import enums
from src import models
from src.services import contacts as contact_services

logger = logging.getLogger(__name__)

_LOG_PREFIX = "[GHL-SERVICE]"


def save_loan_data_to_pool(raw_payload: typing.Dict) -> None:
    logger.info(
        "{} Saving raw payload to the pool for processing (raw_data={}).".format(
            _LOG_PREFIX, raw_payload
        )
    )
    pool_data = models.LoanPool.objects.create(
        status=enums.LoanDataPoolStatus.UNPROCESSED.value,
        status_name=enums.LoanDataPoolStatus.UNPROCESSED.name,
        payload=json.dumps(raw_payload),
    )
    logger.info(
        "{} Saved raw payload to the pool (pool_id={}).".format(
            _LOG_PREFIX, pool_data.id
        )
    )


def process_data_pools() -> None:
    pools_to_process = models.LoanPool.objects.filter(
        status=enums.LoanDataPoolStatus.UNPROCESSED.value
    )
    if not pools_to_process:
        logger.info(
            "{} No UNPROCESSED pools found in db to process. Exiting.".format(
                _LOG_PREFIX
            )
        )
        return

    logger.info(
        "{} Started processing {} UNPROCESSED data pools.".format(
            _LOG_PREFIX, len(pools_to_process)
        )
    )

    for data_pool in pools_to_process:
        try:
            process_data_pool(data_pool=data_pool, skip_duplicate_contact_creation=True)
        except Exception as e:
            msg = "Unexpected exception while processing data pool (id={}). Error: {}".format(
                data_pool.id, common_utils.get_exception_message(exception=e)
            )
            logger.exception("{} {}.".format(_LOG_PREFIX, msg))
            # TODO: SEND MAIL ?
            continue

    logger.info("{} Finished processing UNPROCESSED data pools.".format(_LOG_PREFIX))


def process_data_pool(
    data_pool: models.LoanPool, skip_duplicate_contact_creation: bool = False
) -> None:
    logger.info(
        "{} Processing data pool (id={}, skip_duplicate_contact_creation={}).".format(
            _LOG_PREFIX, data_pool.id, skip_duplicate_contact_creation
        )
    )
    pool_content = simplejson.loads(data_pool.payload)
    contacts = contact_services.get_contacts_by_email(email=pool_content["Email"])

    if not contacts:
        logger.info(
            "{} No contacts fetched from GHL API (email={}).".format(
                _LOG_PREFIX, pool_content["Email"]
            )
        )
        contact_services.create_contact(loan_pool=data_pool)
        return

    logger.info(
        "{} Fetched {} contacts from GHL API to check (email={}).".format(
            _LOG_PREFIX, len(contacts), pool_content["Email"]
        )
    )

    number_of_contacts_created = 0
    for contact in contacts:
        if number_of_contacts_created >= 1:
            break

        loan_id = _get_contact_load_id(data=contact.get("customField", []))
        if not skip_duplicate_contact_creation and pool_content["LoanId"] != loan_id:
            contact_services.create_contact(loan_pool=data_pool)
            number_of_contacts_created += 1
            continue

        contact_services.update_contact(contact=contact, loan_pool=data_pool)

    logger.info(
        "{} Finished processing data pool (id={}, skip_duplicate_contact_creation={}).".format(
            _LOG_PREFIX, data_pool.id, skip_duplicate_contact_creation
        )
    )


def _get_contact_load_id(data: typing.List[typing.Dict]) -> typing.Optional[str]:
    for custom_field in data:
        if custom_field["id"] == enums.ContactCustomField.LOAN_ID.value:
            return str(custom_field["value"])

    return None
