import logging
import typing

import simplejson
from django import http
from django import views

from src.services import loan_data_pool as loan_data_pool_service

logger = logging.getLogger(__name__)

_LOG_PREFIX = "[LOAN-DATA-POOL-VIEW]"


class LoanDataPool(views.View):
    def post(
        self, request: http.HttpRequest, *args: typing.Any, **kwargs: typing.Any
    ) -> http.HttpResponse:
        logger.info(
            "{} Received load data payload to save to pool.".format(_LOG_PREFIX)
        )
        try:
            payload = simplejson.loads(request.body.decode("utf-8"))
        except Exception:
            return http.HttpResponse(
                headers={"Content-Type": "application/json"},
                content=simplejson.dumps(
                    {"error": {"title": "Payload is not valid json."}}
                ),
                status=400,
            )

        """
            TODO::
                1. Validate data
        """

        try:
            loan_data_pool_service.save_loan_data_to_pool(raw_payload=payload)
        except Exception:
            return http.HttpResponse(
                headers={"Content-Type": "application/json"},
                content=simplejson.dumps({"error": {"title": "Internal server error"}}),
                status=500,
            )

        logger.info("{} Successfully processed loan data to pool.")

        return http.HttpResponse(
            headers={"Content-Type": "application/json"},
            content=simplejson.dumps({"data": {"attributes": payload}}),
            status=201,
        )
