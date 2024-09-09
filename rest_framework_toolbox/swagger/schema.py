from rest_framework_toolbox.core.utils import import_class

from rest_framework import serializers
from django.conf import settings

from drf_spectacular.utils import extend_schema, OpenApiRequest, OpenApiResponse, OpenApiExample, OpenApiParameter


# Schema template:
# Specify all possbile `extend_schema` parameters with their default values:
template = {
    "operation_id": None,
    "summary": "",
    "description": None,
    # dict or serializer class or OpenApiRequest
    "request": OpenApiRequest(
        request=None,
        encoding=None,
        examples=None
    ),
    "responses": {
        200: OpenApiResponse(
            # dict or serializer
            response=None,
            # str
            description="Success response",
            # dict
            examples=None
        ),
        400: OpenApiResponse(
            response=None,
            description="Bad request",
            examples=None
        ),
        401: OpenApiResponse(
            response=None,
            description="Unauthorized",
            examples=None
        ),
        403: OpenApiResponse(
            response=None,
            description="Forbidden",
            examples=None
        ),
        404: OpenApiResponse(
            response=None,
            description="Not found",
            examples=None
        ),
        500: OpenApiResponse(
            response=None,
            description="Internal server error",
            examples=None
        )
    },
    "auth": None,
    "tags": None,
    "exclude": False,
    "parameters": None,
    "examples": None
}





def parse_parameter(*args, **kwargs):
    """
    Parses the parameter from the schema
    """
    return OpenApiParameter(
        name=kwargs.get('name', "None"),
        type=kwargs.get('type', str),
        location=kwargs.get('location', 'query'),
        required=kwargs.get('required', False),
        description=kwargs.get('description', ""),
        default=kwargs.get('default', None),
        pattern=kwargs.get('pattern', None),
        enum=kwargs.get('enum', None),
        deprecated=kwargs.get('deprecated', False),
        response=kwargs.get('response', None),
        examples=kwargs.get('examples', None)
    )


def parse_example(*args, **kwargs):
    """
    Parses the example from the schema
    """
    return OpenApiExample(
        name=kwargs.get('name', ""),
        summary=kwargs.get('summary', ""),
        external_value=kwargs.get('external_value', None),
        value=kwargs.get("value", None),
        request_only=kwargs.get("request_only", False),
        response_only=kwargs.get("response_only", False),
        parameter_only=kwargs.get("parameter_only", None),
        status_codes=kwargs.get('status_codes', [])
    )


def parse_response(*args, **kwargs):
    """
    Parses the response from the schema
    """
    return OpenApiResponse(
        response=kwargs.get('response', None),
        description=kwargs.get("description", ""),
        examples=kwargs.get("examples", [])
    )


def generate_schema(*args, **kwargs):
    """
    Generates the schema from the class
    """
    return extend_schema(
        operation_id=kwargs.get("operation_id", ""),
        description=kwargs.get("description", ""),
        summary=kwargs.get("summary", ""),
        external_docs=kwargs.get("external_docs", ""),
        tags=kwargs.get("tags", []),
        versions=kwargs.get("versions", None),
        exclude=kwargs.get("exclude", False),
        request=kwargs.get("request", None),
        methods=kwargs.get("methods", []),
        auth=kwargs.get("auth", None),
        parameters=kwargs.get("parameters", None),
        responses=kwargs.get("responses", None),
        examples=kwargs.get("examples", None),
        callbacks=kwargs.get("callbacks", None),
        extensions=kwargs.get("extensions", None),
        deprecated=kwargs.get("deprecated", False)
    )
