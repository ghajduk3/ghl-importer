import decimal
import typing

import requests
import logging
import simplejson
from urllib import parse as url_parser

from django.conf import settings

from common import enums as common_enums
from common import utils as common_utils
from src.clients.ghl import exceptions

logger = logging.getLogger(__name__)


class GoHighLevelAPIClient(object):
    API_BASE_URL = settings.GHL_BASE_API_URL
    API_AUTH_TOKEN = settings.GHL_API_AUTHENTICATION_TOKEN
    VALID_STATUS_CODES = [200, 201]

    LOG_PREFIX = "[GHL-API-CLIENT]"

    def get_contacts(self, email: str) -> typing.List[typing.Dict]:
        return simplejson.loads(
            self._request(
                endpoint="v1/contacts/lookup",
                method=common_enums.HttpMethod.GET,
                params={"email": email},
            ).content,
            parse_float=decimal.Decimal,
        )["contacts"]

    def create_contact(
        self,
        email: str,
        first_name: typing.Optional[str] = None,
        last_name: typing.Optional[str] = None,
        custom_fields: typing.Optional[typing.Dict] = None,
        phone: typing.Optional[str] = None,
        address: typing.Optional[str] = None,
        city: typing.Optional[str] = None,
        state: typing.Optional[str] = None,
        postal_code: typing.Optional[str] = None,
        website: typing.Optional[str] = None,
        timezone: typing.Optional[str] = None,
        dnd: typing.Optional[bool] = None,
        tags: typing.Optional[typing.List[str]] = None,
        source: typing.Optional[str] = None,
    ) -> typing.Dict:
        payload = {"email": email}

        if first_name:
            payload["firstName"] = first_name

        if last_name:
            payload["lastName"] = last_name

        if custom_fields:
            payload["customField"] = custom_fields

        if phone:
            payload["phone"] = phone

        if address:
            payload["address1"] = address

        if city:
            payload["city"] = city

        if state:
            payload["state"] = state

        if postal_code:
            payload["postalCode"] = postal_code

        if website:
            payload["website"] = website

        if timezone:
            payload["timezone"] = timezone

        if dnd:
            payload["dnd"] = dnd

        if tags:
            payload["tags"] = tags

        if source:
            payload["source"] = source

        return simplejson.loads(
            self._request(
                endpoint="v1/contacts/",
                method=common_enums.HttpMethod.POST,
                payload=payload,
            ).content,
            parse_float=decimal.Decimal,
        )["contact"]

    def update_contact(
        self,
        contact_id: str,
        email: typing.Optional[str] = None,
        first_name: typing.Optional[str] = None,
        last_name: typing.Optional[str] = None,
        custom_fields: typing.Optional[typing.Dict] = None,
        phone: typing.Optional[str] = None,
        address: typing.Optional[str] = None,
        city: typing.Optional[str] = None,
        state: typing.Optional[str] = None,
        postal_code: typing.Optional[str] = None,
        website: typing.Optional[str] = None,
        timezone: typing.Optional[str] = None,
        dnd: typing.Optional[bool] = None,
        tags: typing.Optional[typing.List[str]] = None,
        source: typing.Optional[str] = None,
    ) -> typing.Dict:
        payload = {}

        if email:
            payload["email"] = email

        if first_name:
            payload["firstName"] = first_name

        if last_name:
            payload["lastName"] = last_name

        if custom_fields:
            payload["customField"] = custom_fields

        if phone:
            payload["phone"] = phone

        if address:
            payload["address1"] = address

        if city:
            payload["city"] = city

        if state:
            payload["state"] = state

        if postal_code:
            payload["postalCode"] = postal_code

        if website:
            payload["website"] = website

        if timezone:
            payload["timezone"] = timezone

        if dnd:
            payload["dnd"] = dnd

        if tags:
            payload["tags"] = tags

        if source:
            payload["source"] = source

        return simplejson.loads(
            self._request(
                endpoint="v1/contacts/{}".format(contact_id),
                method=common_enums.HttpMethod.PUT,
                payload=payload,
            ).content,
            parse_float=decimal.Decimal,
        )["contact"]

    def _request(
        self,
        endpoint: str,
        method: common_enums.HttpMethod,
        params: typing.Optional[dict] = None,
        payload: typing.Optional[dict] = None,
    ) -> requests.Response:
        url = url_parser.urljoin(base=self.API_BASE_URL, url=endpoint)
        try:
            response = requests.request(
                url=url,
                method=method.value,
                params=params,
                json=payload,
                headers=self._get_request_headers(),
            )

            if response.status_code not in self.VALID_STATUS_CODES:
                msg = "Invalid API client response (status_code={}, data={})".format(
                    response.status_code,
                    response.content.decode(encoding="utf-8"),
                )
                logger.error("{} {}.".format(self.LOG_PREFIX, msg))
                raise exceptions.GoHighLevelAPIBadResponseCodeError(
                    message=msg, code=response.status_code
                )

            logger.debug(
                "{} Successful response (endpoint={}, status_code={}, payload={}, params={}, raw_response={}).".format(
                    self.LOG_PREFIX,
                    endpoint,
                    response.status_code,
                    payload,
                    params,
                    response.content.decode(encoding="utf-8"),
                )
            )
        except requests.exceptions.ConnectTimeout as e:
            msg = "Connect timeout. Error: {}".format(
                common_utils.get_exception_message(exception=e)
            )
            logger.exception("{} {}.".format(self.LOG_PREFIX, msg))
            raise exceptions.GoHighLevelAPIException(msg)
        except requests.RequestException as e:
            msg = "Request exception. Error: {}".format(
                common_utils.get_exception_message(exception=e)
            )
            logger.exception("{} {}.".format(self.LOG_PREFIX, msg))
            raise exceptions.GoHighLevelAPIException(msg)

        return response

    @classmethod
    def _get_request_headers(cls) -> typing.Dict:
        return {
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(cls.API_AUTH_TOKEN),
        }
