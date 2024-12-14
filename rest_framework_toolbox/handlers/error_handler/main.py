from typing import Any, Dict, TypeVar, Callable
from rest_framework_toolbox.core.models import JSONModel
from rest_framework_toolbox.core.utils import import_class, get_class_fields, camel_to_snake

from ._config import configs

import logging

__testing = configs['test']

if not __testing:
    from rest_framework.exceptions import APIException
    from rest_framework.response import Response
    from rest_framework.views import exception_handler as drf_exception_handler
    from django.conf import settings


__all__ = [
    "ErrorHandler",
]

if __testing:
    APIException = TypeVar("APIException")
    Response = TypeVar("Response")


# def register_handler(exception_class):
#         def decorator(func):
#             ErrorHandler._user_handlers[exception_class.__name__] = func
#             return func
#         return decorator

class ErrorHandler:
    _default_handlers = [
        'ParseError',
        'NotAuthenticated',
        'AuthenticationFailed',
        'InvalidToken',
        'ValidationError',
        'NotFound',
        'Throttled',
        'MethodNotAllowed',
        'PermissionDenied',
        'ServiceUnavailable',
        'Http404',
    ]

    _user_handlers = {}

    class Config:
        use_drf_handler = False

    def __init__(self, error_model=None) -> None:
        if error_model:
            assert issubclass(
                error_model, JSONModel), "error_model must be an extension to JSONModel"
        self.error_model = error_model
        self.context = None
        self.exc = None
        self.response = None
        self.logger = ErrorHandler.register_logger()
        self.crash_logger = ErrorHandler.register_crash_logger()
        self.signals = ErrorHandler.register_signals()

    @classmethod
    def register_handler(cls, exception_class):
        def decorator(func):
            cls._user_handlers[exception_class.__name__] = func
            return func
        return decorator

    @classmethod
    def register_exception(cls, exception: APIException):
        @cls.register_handler(exception)
        def handler(exc, context, res):
            res.message = exc.outcome
            res.data = {
                'code': exc.get_full_details()['code'],
                'details': exc.get_full_details()['message']
            }

            return res

    @classmethod
    def register_exceptions(cls, exceptions: list):
        for exception in exceptions:
            cls.register_exception(exception)

    @staticmethod
    def get_error_model(view=None):
        if view and hasattr(view, 'error_model'):
            return view.error_model
        elif getattr(settings, 'ERROR_JSON_MODEL', None):
            return import_class(settings.ERROR_JSON_MODEL)
        else:
            raise Exception("A global error json model must be set")

    @classmethod
    def register_signals(self):
        signals = getattr(settings, 'ERROR_HANDLER_SIGNALS', None)

        if type(signals) == list:
            return signals

    @classmethod
    def register_logger(self):
        logger = getattr(settings, 'ERROR_HANDLER_LOGGER', None)

        if logger:
            return import_class(logger)
        return logging.getLogger('rest_framework_toolbox_error_logger')

    @classmethod
    def register_crash_logger(self):
        crash_logger = getattr(settings, 'ERROR_HANDLER_CRASH_LOGGER', None)

        if crash_logger:
            return import_class(crash_logger)
        else:
            return logging.getLogger('rest_framework_toolbox_crash_logger')

    def _convert_to_apiexception(self, exc):
        return APIException(

        )

    def _get_error_model_fields(self) -> dict:
        """Returns all model instance atrributes and their types"""
        fields = []
        for attr in dir(self.error_model):
            if callable(getattr(self.error_model, attr)) and issubclass(getattr(self.error_model, attr).__class__, JSONModel):
                fields.append(attr)
            elif not callable(getattr(self.error_model, attr)) and not attr.startswith("__") and not attr.startswith("_"):
                fields.append(attr)
            else:
                pass
        return fields

    def override_default_handler(self, exception_name: str, handler: Callable) -> None:
        self._default_handlers[exception_name] = handler

    def _handle_with_registered_handler(self, exception_name: str, exc, context, response):
        if exception_name in self._user_handlers:
            user_handler = self._user_handlers[exception_name]
            # User handler must return an instance of `self.error_model` class
            error_res = user_handler(exc, context, response)
            assert isinstance(
                error_res, self.error_model), "User-defined handler must return an instance of the error model"

            return error_res

        return None

    def _handle_with_predefined_handler(self, exception_class: str, exc, context, response):
        if exception_class in self._default_handlers:
            # print("Handling default exception")
            error_res = self.error_model()

            # Handle default exception using handler defined in error_res
            if getattr(error_res, camel_to_snake(exception_class), None):
                handler = getattr(
                    error_res, camel_to_snake(exception_class), None)
                if callable(handler):
                    error_res = handler(context['request'], response)
                    if error_res:
                        assert isinstance(error_res, self.error_model), \
                            "User-defined handler must return an instance of the error model"
                        return error_res

            return None

    def _handle(self, exc: APIException, context: Dict, response: Response) -> JSONModel:
        """
        Django REST API Error handler

        In the upcoming sections, between parantheses defined the phase name, in which a signal can be registered

        # Handling API exceptions goes in these phases:
        ----------------------------------------
        ## Initialization (init)
        -------------------------
        - Get the view that threw the error
        - Get the exception class name
        - Instantiate the error json model

        ## Error Handling (error_handling)
        ----------------------------------
        ### Handling with registered handlers
        -------------------------------------
        - Check if the user registered any custom handler against the exception
        - If a handler is found, call it and return the result

        ### Handle non APIException errors
        ----------------------------------
        - Check if the exception is an instance of Http404 which is a standard exception but not an APIException
        - Check if the custom exception has its own handler and return it

        ### Handle exception with view's `on_error` func
        --------------------------------------------
        - Check if the view has an `on_error` method
        - If `on_error` is defined, call it and return the result

        ### Fallback to default handlers
        ---------------------------------
        - If no handler is defined, or `on_error` failed to handle.
        - Handle the error using the exception class user supplied attributes

        ## Failure to handle error (failure)
        ------------------------------------
        - If no handler is defined, raise an exception
        ---------------------------

        """
        self.context = context
        self.exc = exc
        if response:
            self.response = response
        view = context.get('view', None)
        exception_class = exc.__class__.__name__
        error_res = None

        assert view, "View is required to handle exceptions"
        assert self.error_model, "Error model is required to handle exceptions"
        
        if response.status_code > 499:
            self.report_crash()

        # 1. Check if the user registered any custom handler against the exception
        error_res = self._handle_with_registered_handler(
            exception_class, exc, context, response)
        if error_res:
            self._post_handling_processing()
            return error_res

        # If the error is an instance of Http404 which is a standard exception but not an APIException
        if exception_class == 'Http404':
            error_res = self._handle_with_predefined_handler(
                exception_class, exc, context, response)

            if error_res:
                self._post_handling_processing()
                return error_res

        elif exception_class == 'ServiceUnavailable':
            error_res = self._handle_with_predefined_handler(
                exception_class, exc, context, response)

            if error_res:
                self._post_handling_processing()
                return error_res

        # 2. Check if the exception can be handled by view's 'on_error' method
        if getattr(view, 'on_error', None) and isinstance(exc, APIException):
            serializer_error_handler = getattr(view, 'on_error', None)
            if serializer_error_handler and callable(serializer_error_handler):
                error_res = serializer_error_handler(exc, context, response)

            if error_res:
                assert isinstance(error_res, self.error_model), \
                    "User-defined handler must return an instance of the error model"
                self._post_handling_processing()
                return error_res

        # 3. Fallback to default handlers defined in error_res if no `on_error` is defined
        error_res = self._handle_with_predefined_handler(
            exception_class, exc, context, response)

        if error_res:
            self._post_handling_processing()
            return error_res

        # 3. If no handler is defined, handle the error using the exception class user supplied attributes
        else:
            self.report_crash()
            error_res = self.error_model()

        # 4. Postprocessing
        if error_res:
            self._post_handling_processing()
            return error_res
        else:
            raise Exception(f"Error could not be handled:\n{str(exc)}")

    def _post_handling_processing(self):
        view = None
        request = None
        if self.context:
            view = self.context.get('view', None)
            request = self.context.get('request', None)
        if view and request:
            try:
                req_data = request.data
            except:
                req_data = None
                req_method = None
                uri = None
                meta = None
            req_method = getattr(request, 'method', None)
            uri = getattr(request, 'path_info', None)
            meta = getattr(request, 'META', None)
            
            import traceback

            self.logger.warn(
                f'Exception raised in {view.__class__.__name__} during handling {req_method} {uri} {req_data} {meta} - Taceback: {traceback.format_exc()}')

    def report_crash(self):
        import traceback
        traceback_str = traceback.format_exc()
        request = self.context.get('request', None)
        method = None

        if request:
            method = request.method
            req_data = getattr(request, 'data', None)
            req_meta = getattr(request, 'META', None)
            request = request.build_absolute_uri()

        view = self.context.get('view', None)
        
        if view:
            view = view.__class__.__name__
            
        exception_name = self.exc.__class__.__name__
        
        self.crash_logger.error(
                            "--- Error crash report --- "
                            f"\nError context:\n" 
                            "------------------\n"
                            f"Request Header:\n{method} {request}\n\n"
                            f"Request Data:\n{req_data}\n\n"
                            f"Request META:\n{req_meta}\n\n"
                            f"Action Name:\n{view}\n\n"
                            f"Exception Class:\n{exception_name}\n\n"
                            f"Traceback Record:\n{traceback_str}\n\n"
                            )

    @staticmethod
    def handle_exception(exc, context) -> Response:
        print(f"Handling exception: {exc.__class__.__name__}")
        # WARNING: Don't remove the default handler as it performs DB rollback and init headers
        self = ErrorHandler()
        response = drf_exception_handler(exc, context)
        self.error_model = self.get_error_model(view=context['view'])
        assert self.error_model, "Error model must be set"
        assert issubclass(
            self.error_model, JSONModel), "error_model must be an extension to JSONModel"

        try:
            error_res = self._handle(exc, context, response)
            if error_res:
                response.data = error_res.to_dict()
                if getattr(exc, 'headers', None):
                    response.headers.update(exc.headers)
                return response
        except:
            # TODO capture traceback and log this error, then send it to sentry/PROMETHEOUS
            import traceback
            traceback.print_exc()
            response.status_code = 500
            response.data = {
                'code': 'Error in handling error',
                'details': 'An unexpected error occurred during handling an error.'
            }
            return response
