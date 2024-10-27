from typing import Any

from django.conf import settings

from rest_framework import serializers

from rest_framework_toolbox.core.models import JSONModel
from rest_framework_toolbox.core.utils import import_class
from rest_framework_toolbox.core import fields


from drf_spectacular.utils import (
    extend_schema,
    OpenApiRequest,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiExample,
    inline_serializer
)

from .schema_errors import SchemaSuccess, SchemaError


class Schema:
    def __init__(self) -> None:
        pass

    @staticmethod
    def generate_schema(schema):
        operation_id = getattr(schema, "operation_id", None)
        description = getattr(schema, "description", None)
        summary = getattr(schema, "summary", None)
        tags = getattr(schema, "tags", None)
        external_docs = getattr(schema, 'external_docs', None)
        methods = getattr(schema, "methods", None)
        auth = getattr(schema, "auth", None)
        request = getattr(schema, 'request', None)
        parameters = getattr(schema, 'parameters', None)
        responses = getattr(schema, 'responses', None)
        examples = getattr(schema, 'examples', None)

        gen_request = None
        gen_auth = []
        gen_parameters = []
        gen_responses = {}
        gen_examples = []

        # Add request
        if request:
            if isinstance(request, (OpenApiRequest, serializers.Serializer)):
                gen_request = request

        # Add auth
        if auth:
            if isinstance(auth, (list, tuple)):
                for a in auth:
                    gen_auth.append(a)
            elif isinstance(auth, serializers.Serializer):
                gen_auth.append(auth)

        # Add parameters
        if parameters:
            for param in parameters:
                if isinstance(param, OpenApiParameter):
                    gen_parameters.append(param)

        # Add success responses
        if responses:
            for status, response in responses.items():
                if isinstance(response, (OpenApiResponse, dict, serializers.Serializer)):
                    gen_responses[status] = response

        # Add examples
        if examples:
            for example in examples:
                if isinstance(example, OpenApiExample):
                    gen_examples.append(example)

        if not auth:
            return extend_schema(
                operation_id=operation_id,
                description=description,
                summary=summary,
                tags=tags,
                external_docs=external_docs,
                methods=methods,
                request=gen_request,
                parameters=gen_parameters,
                responses=gen_responses,
                examples=gen_examples
            )

        return extend_schema(
            operation_id=operation_id,
            description=description,
            summary=summary,
            tags=tags,
            external_docs=external_docs,
            auth=gen_auth,
            methods=methods,
            request=gen_request,
            parameters=gen_parameters,
            responses=gen_responses,
            examples=gen_examples
        )


def generate_success_schema(serializer_name="SuccessSchema", response=None):
    """
    Generates a DRF serializer from JSONModel fields to be plugged into a serializer class

    response: is a dict of value/serializers for the field in the Success JSONModel.

    You must provide a response field in case if your response model contains `DataField` or a class that extends `JSONModel` 
    """
    success_class = import_class(settings.SUCCESS_JSON_MODEL)
    assert issubclass(
        success_class, JSONModel), "SUCCESS_JSON_MODEL class must be an instance of JSONModel class"

    serializer_fields = {}

    for field_name, field_value in success_class._fields.items():
        # Inspect `response`
        if field_name in response.keys():

            # if response[name] is a serializer, add it to `serializer_fields`
            if isinstance(response[field_name], serializers.Serializer):
                serializer_fields[field_name] = response[field_name]

            # if response[name] is an object/value, get its serializer and add its default value
            else:
                # provide default value to the serializer
                serializer_fields[field_name] = field_value.serializer(
                    response[field_name])
        # Use default value
        else:
            serializer_fields[field_name] = field_value.serializer()

    # Create the serializer class
    serializer_cls = type(
        serializer_name,
        (serializers.Serializer,),
        serializer_fields
    )

    return serializer_cls


def generate_error_schema(serializer_name="FailSchema", response=None):
    """
    Generates a DRF serializer for error responses
    """
    fail_class = import_class(settings.ERROR_JSON_MODEL)
    assert issubclass(
        fail_class, JSONModel), "ERROR_JSON_MODEL class must be an instance of JSONModel class"

    serializer_fields = {}

    for field_name, field_value in fail_class._fields.items():
        # Inspect `response`
        if field_name in response.keys():

            # if response[name] is a serializer, add it to `serializer_fields`
            if isinstance(response[field_name], serializers.Serializer):
                serializer_fields[field_name] = response[field_name]

            # if response[name] is an object/value, get its serializer and add its default value
            else:
                # provide default value to the serializer
                serializer_fields[field_name] = field_value.serializer(
                    response[field_name])
        # Use default value
        else:
            serializer_fields[field_name] = field_value.serializer()

    # Create the serializer class
    serializer_cls = type(
        serializer_name,
        (serializers.Serializer,),
        serializer_fields
    )

    return serializer_cls
