from fastapi import status


class APIException(Exception):
    status = status.HTTP_500_INTERNAL_SERVER_ERROR
    message = 'Internal Error Occurs.'
    error_code = 50001

    def __init__(self, status_code=None, message=None, error_code=None):
        if status_code is not None: self.status = status_code
        if message is not None: self.message = message
        if error_code is not None: self.error_code = error_code


class PermissionDeniedException(APIException):
    status = status.HTTP_401_UNAUTHORIZED
    message = 'Unauthorization.'
    error_code = 40101


class NotFoundException(APIException):
    status = status.HTTP_404_NOT_FOUND
    message = 'Not Found.'
    error_code = 40401


class InvalidCredentialsException(APIException):
    status = status.HTTP_401_UNAUTHORIZED
    message = 'Invalid Credentials.'
    error_code = 40102


class InvalidRequestException(APIException):
    status = status.HTTP_400_BAD_REQUEST
    message = 'Invalid Request.'
    error_code = 40001


class DuplicateEntryException(APIException):
    status = status.HTTP_409_CONFLICT
    message = 'Duplicate Entry.'
    error_code = 40901


class BadRequestException(APIException):
    status = status.HTTP_400_BAD_REQUEST
    message = 'Bad Request.'
    error_code = 40002


class ForbiddenException(APIException):
    status = status.HTTP_403_FORBIDDEN
    message = 'Forbidden.'
    error_code = 40301


class MethodNotAllowedException(APIException):
    status = status.HTTP_405_METHOD_NOT_ALLOWED
    message = 'Method Not Allowed.'
    error_code = 40501


class UnprocessableEntityException(APIException):
    status = status.HTTP_422_UNPROCESSABLE_ENTITY
    message = 'Unprocessable Entity.'
    error_code = 42201
