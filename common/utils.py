import typing

import marshmallow

from common import exceptions


def get_exception_message(exception: Exception) -> str:
    if isinstance(exception, type):
        return exception.__name__

    if hasattr(exception, "message") and exception.message:
        return exception.message
    return exception.args[0] if len(exception.args) else ""


def validate_data_schema(
    data: typing.Union[typing.Dict, typing.List[typing.Dict]],
    schema: marshmallow.schema.Schema,
) -> typing.Dict:
    try:
        validated_data = schema.load(data=data, unknown=marshmallow.EXCLUDE)
    except marshmallow.exceptions.ValidationError as e:
        raise exceptions.ValidationSchemaException(get_exception_message(exception=e))

    return validated_data
