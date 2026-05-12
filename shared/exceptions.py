"""Global exception handler and custom exceptions."""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


class GirinkaException(Exception):
    """Base custom exception."""
    status_code = status.HTTP_400_BAD_REQUEST
    error_code = "GIRINKA_ERROR"
    default_message = "An error occurred."

    def __init__(self, message=None, error_code=None):
        self.message = message or self.default_message
        if error_code:
            self.error_code = error_code
        super().__init__(self.message)


class InsufficientMilkDataError(GirinkaException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    error_code = "INSUFFICIENT_MILK_DATA"
    default_message = "LSTM requires at least 7 days of milk records."


class CowAlreadyDeceasedError(GirinkaException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    error_code = "COW_ALREADY_DECEASED"
    default_message = "Cannot update a deceased cow."


class BeneficiaryInactiveError(GirinkaException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    error_code = "BENEFICIARY_INACTIVE"
    default_message = "This beneficiary is deregistered."


class PassonPendingError(GirinkaException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    error_code = "PASSON_PENDING"
    default_message = "Cannot deregister while a pass-on transfer is pending."


class DuplicateTagNumberError(GirinkaException):
    status_code = status.HTTP_409_CONFLICT
    error_code = "DUPLICATE_TAG_NUMBER"
    default_message = "This cow tag number already exists."


class DuplicateNationalIdError(GirinkaException):
    status_code = status.HTTP_409_CONFLICT
    error_code = "DUPLICATE_NATIONAL_ID"
    default_message = "This national ID is already registered."


class InvalidUbudehe(GirinkaException):
    status_code = status.HTTP_400_BAD_REQUEST
    error_code = "INVALID_UBUDEHE"
    default_message = "Girinka program only accepts Ubudehe categories 1 and 2."


class ModelNotDeployedError(GirinkaException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    error_code = "MODEL_NOT_DEPLOYED"
    default_message = "No active ML model available for this prediction type."


class PredictionFailedError(GirinkaException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    error_code = "PREDICTION_FAILED"
    default_message = "ML service returned an error."


class SMSDeliveryFailedError(GirinkaException):
    status_code = status.HTTP_502_BAD_GATEWAY
    error_code = "SMS_DELIVERY_FAILED"
    default_message = "SMS could not be delivered via Africa's Talking."


def girinka_exception_handler(exc, context):
    """Custom DRF exception handler — wraps all errors in standard format."""
    if isinstance(exc, GirinkaException):
        return Response(
            {"detail": exc.message, "error_code": exc.error_code},
            status=exc.status_code,
        )
    response = exception_handler(exc, context)
    if response is not None:
        logger.error(f"API Error: {exc}", exc_info=True)
        return response
    logger.critical(f"Unhandled exception: {exc}", exc_info=True)
    return Response(
        {"detail": "Internal server error.", "error_code": "INTERNAL_ERROR"},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
