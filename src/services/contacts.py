import logging
import typing

import simplejson
from django.db import transaction

from common import utils as common_utils
from src import enums
from src import exceptions
from src import models
from src.clients.ghl import client as ghl_api_client
from src.clients.ghl import exceptions as ghl_api_exceptions

logger = logging.getLogger(__name__)
_LOG_PREFIX = "[GHL-CONTACTS]"


def get_contacts_by_email(email: str) -> typing.List[typing.Dict]:
    logger.info('{} Fetching all contacts for email "{}".'.format(_LOG_PREFIX, email))

    try:
        contacts = ghl_api_client.GoHighLevelAPIClient().get_contacts(email=email)
    except ghl_api_exceptions.GoHighLevelAPIException as e:
        msg = "Unable to fetch contacts from GHL API. Error: {}".format(
            common_utils.get_exception_message(exception=e)
        )
        logger.exception("{} {}.".format(_LOG_PREFIX, msg))
        raise exceptions.GoHighLevelAPIClientError(msg)

    logger.info(
        '{} Fetched {} contacts for email "{}".'.format(
            _LOG_PREFIX, len(contacts), email
        )
    )
    return contacts


def create_contact(loan_pool: models.LoanPool) -> None:
    if loan_pool.status != enums.LoanDataPoolStatus.UNPROCESSED.value:
        logger.info(
            "{} Cannot create new contact, loan pool (id={}) not in status {}. Exiting.".format(
                _LOG_PREFIX, loan_pool.id, enums.LoanDataPoolStatus.UNPROCESSED.name
            )
        )
        return

    raw_contact = simplejson.loads(loan_pool.payload)
    logger.info(
        "{} Creating new contact (loan_pool_id={}, raw_contact_data={}).".format(
            _LOG_PREFIX, loan_pool.id, raw_contact
        )
    )

    custom_fields = _prepare_contact_custom_fields(raw_contact=raw_contact)
    try:
        contact = ghl_api_client.GoHighLevelAPIClient().create_contact(
            email=raw_contact["Email"],
            first_name=raw_contact.get("FirstName"),
            last_name=raw_contact.get("LastName"),
            phone=raw_contact.get("DayPhone"),
            address=raw_contact.get("Street"),
            city=raw_contact.get("City"),
            state=raw_contact.get("State"),
            postal_code=raw_contact.get("ZipCode"),
            custom_fields=custom_fields,
        )
    except ghl_api_exceptions.GoHighLevelAPIException as e:
        msg = "Unable to create contact (email={}). Error: {}".format(
            raw_contact["Email"], common_utils.get_exception_message(exception=e)
        )
        logger.exception("{} {}.".format(_LOG_PREFIX, msg))
        raise exceptions.GoHighLevelAPIClientError(msg)

    contact_id = contact["id"]

    logger.info(
        "{} Created new contact (loan_pool_id={}, id={}) on GoHighLevel.".format(
            _LOG_PREFIX, loan_pool.id, contact_id
        )
    )

    with transaction.atomic():
        loan_pool.status = enums.LoanDataPoolStatus.PROCESSED.value
        loan_pool.status_name = enums.LoanDataPoolStatus.PROCESSED.name
        loan_pool.save(update_fields=["status", "status_name", "updated_at"])

        db_contact = models.Contact.objects.filter(contact_id=contact_id).first()

        if not db_contact:
            db_contact = models.Contact.objects.create(contact_id=contact_id)

        contact_history = models.ContactHistory.objects.create(
            contact=db_contact,
            pool=loan_pool,
            action=enums.ContactAction.CREATED.value,
            action_name=enums.ContactAction.CREATED.name,
            action_data=simplejson.dumps(contact),
        )

    logger.info(
        "{} Saved contact to the db (contact_id={}, contact_history_id={}).".format(
            _LOG_PREFIX, db_contact.id, contact_history.id
        )
    )


def update_contact(contact: typing.Dict, loan_pool: models.LoanPool) -> None:
    logger.info(
        "{} Updating contact (contact_id={}, loan_pool_id={}).".format(
            _LOG_PREFIX, contact["id"], loan_pool.id
        )
    )
    loan_pool_content = simplejson.loads(loan_pool.payload)
    content_to_update = _prepare_contact_update_fields(
        contact=contact, data_pool_content=loan_pool_content
    )

    try:
        updated_contact = ghl_api_client.GoHighLevelAPIClient().update_contact(
            contact_id=contact["id"],
            **content_to_update,
        )
    except ghl_api_exceptions.GoHighLevelAPIException as e:
        msg = "Unable to update contact (contact_id={}). Error: {}".format(
            contact["id"], common_utils.get_exception_message(exception=e)
        )
        logger.exception("{} {}.".format(_LOG_PREFIX, msg))
        raise exceptions.GoHighLevelAPIClientError(msg)

    logger.info(
        "{} Updated contact (id={}, content_to_update={}, updated_contact={}).".format(
            _LOG_PREFIX, contact["id"], content_to_update, updated_contact
        )
    )

    with transaction.atomic():
        loan_pool.status = enums.LoanDataPoolStatus.PROCESSED.value
        loan_pool.status_name = enums.LoanDataPoolStatus.PROCESSED.name
        loan_pool.save(update_fields=["status", "status_name", "updated_at"])

        db_contact = models.Contact.objects.filter(contact_id=contact["id"]).first()

        if not db_contact:
            db_contact = models.Contact.objects.create(contact_id=contact["id"])

        contact_history = models.ContactHistory.objects.create(
            contact=db_contact,
            pool=loan_pool,
            action=enums.ContactAction.UPDATED.value,
            action_name=enums.ContactAction.UPDATED.name,
            action_data=simplejson.dumps(content_to_update),
        )

    logger.info(
        "{} Saved updated contact to the db (contact_id={}, contact_history_id={}).".format(
            _LOG_PREFIX, db_contact.id, contact_history.id
        )
    )


def _prepare_contact_update_fields(
    contact: typing.Dict, data_pool_content: typing.Dict
) -> typing.Dict:
    fields_to_update = {
        "email": None
        if data_pool_content["Email"] == contact.get("email")
        else data_pool_content["Email"],
        "first_name": None
        if not data_pool_content.get("FirstName")
        or data_pool_content.get("FirstName") == contact.get("firstName")
        else data_pool_content.get("FirstName"),
        "last_name": None
        if not data_pool_content.get("LastName")
        or data_pool_content.get("LastName") == contact.get("lastName")
        else data_pool_content.get("LastName"),
        "phone": None
        if not data_pool_content.get("DayPhone")
        or data_pool_content.get("DayPhone") == contact.get("phone")
        else data_pool_content.get("DayPhone"),
        "address": None
        if not data_pool_content.get("Street")
        or data_pool_content.get("Street") == contact.get("address1")
        else data_pool_content.get("Street"),
        "city": None
        if not data_pool_content.get("City")
        or data_pool_content.get("City") == contact.get("city")
        else data_pool_content.get("City"),
        "state": None
        if not data_pool_content.get("State")
        or data_pool_content.get("State") == contact.get("state")
        else data_pool_content.get("State"),
        "postal_code": None
        if not data_pool_content.get("ZipCode")
        or data_pool_content.get("ZipCode") == contact.get("postalCode")
        else data_pool_content.get("ZipCode"),
    }

    data_pool_content_custom_fields = _prepare_contact_custom_fields(
        raw_contact=data_pool_content
    )
    contact_custom_fields = {
        custom_field["id"]: custom_field["value"]
        for custom_field in contact.get("customField", [])
    }
    data_pool_content_custom_field_names = list(data_pool_content_custom_fields.keys())
    contact_custom_fields_names = list(contact_custom_fields.keys())
    data_pool_content_custom_field_names.extend(contact_custom_fields_names)
    custom_fields = {
        key: data_pool_content_custom_fields[key]
        if key in data_pool_content_custom_fields
        else contact_custom_fields.get(key)
        for key in set(data_pool_content_custom_field_names)
    }

    fields_to_update["custom_fields"] = custom_fields
    return fields_to_update


def _prepare_contact_custom_fields(raw_contact: typing.Dict) -> typing.Dict:
    custom_fields = {}
    if raw_contact.get("LeadStage"):
        custom_fields[enums.ContactCustomField.LEAD_STAGE.value] = raw_contact[
            "LeadStage"
        ]

    if raw_contact.get("PropertyZipCode"):
        custom_fields[
            enums.ContactCustomField.SUBJECT_PROPERTY_ZIP_CODE.value
        ] = raw_contact["PropertyZipCode"]

    if raw_contact.get("PropertyStreet"):
        custom_fields[
            enums.ContactCustomField.SUBJECT_PROPERTY_ADDRESS.value
        ] = raw_contact["PropertyStreet"]

    if raw_contact.get("PropertyCity"):
        custom_fields[
            enums.ContactCustomField.SUBJECT_PROPERTY_CITY.value
        ] = raw_contact["PropertyCity"]

    if raw_contact.get("PropertyState"):
        custom_fields[
            enums.ContactCustomField.SUBJECT_PROPERTY_STATE.value
        ] = raw_contact["PropertyState"]

    if raw_contact.get("ContactId"):
        custom_fields[enums.ContactCustomField.CONTACT_ID.value] = raw_contact[
            "ContactId"
        ]

    if raw_contact.get("OriginatorName"):
        custom_fields[enums.ContactCustomField.LOAN_OFFICER_NAME.value] = raw_contact[
            "OriginatorName"
        ]

    if raw_contact.get("OriginatorBusinessEmail"):
        custom_fields[enums.ContactCustomField.LOAN_OFFICER_EMAIL.value] = raw_contact[
            "OriginatorBusinessEmail"
        ]

    if raw_contact.get("LoanStatus"):
        custom_fields[enums.ContactCustomField.LOAN_STATUS.value] = raw_contact[
            "LoanStatus"
        ]

    if raw_contact.get("LoanId"):
        custom_fields[enums.ContactCustomField.LOAN_ID.value] = raw_contact["LoanId"]

    return custom_fields
