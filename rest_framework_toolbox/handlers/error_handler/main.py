from typing import Any, Dict, TypeVar, Callable

from ._config import configs

__testing = configs['test']

if not __testing:
    from rest_framework.exceptions import APIException
    from rest_framework.response import Response
    from rest_framework.views import exception_handler as drf_exception_handler
    from django.conf import settings
    
from rest_framework_toolbox.core.utils import import_class
from rest_framework_toolbox.core.json_model import JSONModel


__all__ = [
    "ErrorHandler",
]

if __testing:
    APIException = TypeVar("APIException")
    Response = TypeVar("Response")

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
        'ServiceUnavailable'
    ]
    
    _user_handlers = {}
    
    class Config:
        use_drf_handler = False
        
    def __init__(self, error_model = None) -> None:
        if error_model:
            assert issubclass(error_model, JSONModel), "error_model must be an extension to JSONModel"
        self.error_model = error_model
        
    @classmethod
    def register_handler(cls, exception_class):
        def decorator(func):
            cls._user_handlers[exception_class.__name__] = func
            return func
        return decorator

    @classmethod
    def register_exception(cls, exception : APIException):
        @cls.register_handler(exception)
        def handler(exc, context, res):
            res.message  = exc.outcome
            res.data = {
                'code': exc.get_full_details()['code'],
                'details': exc.get_full_details()['message']
            }

            return res

    @classmethod
    def register_exceptions(cls, exceptions : list):
        for exception in exceptions:
            cls.register_exception(exception)
    
    @staticmethod
    def get_error_model(view = None):
        if view and hasattr(view, 'error_model'):
            return view.error_model
        elif getattr(settings, 'ERROR_JSON_MODEL', None):
            return import_class(settings.ERROR_JSON_MODEL)
        else:
            raise Exception("A global error json model must be set")
    
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
    
    def _handle(self, exc : APIException, context: Dict, response: Response) -> JSONModel:
        exception_class = exc.__class__.__name__
        error_res = None
        error_data = None
        
        # Check if the exception thrown is DRF default and can be handled by a default handler
        if exception_class in self._default_handlers:
            error_res = self.error_model()
            serializer_error_handler = getattr(error_res, 'serializer_error', None)
            if serializer_error_handler:
                error_res = serializer_error_handler(exc, context, response)
            else:
                error_res = None
                error_data = exc.get_full_details()
        
        # Check if the user registered any custom handler against the exception 
        elif exception_class in self._user_handlers:
            user_handler = self._user_handlers[exception_class]
            # User handler must return an instance of self.error_model class
            error_res = user_handler(exc, context, response)
            assert isinstance(error_res, self.error_model), "User-defined handler must return an instance of the error model"

            return error_res
        
        # If no handler is defined, handle the error using the exception class user supplied attributes    
        else:
            error_response_fields = self._get_error_model_fields()
            error_res = self.error_model()
            
            for field in error_response_fields:
                # Check if the field value is set directly in the exc class
                val = getattr(exc, field, None)
                if val:
                    setattr(error_res, field, val)
                # Check if the field value is set dynamically via get_* method
                else:
                    getter= getattr(exc, f'get_{field}', None)
                    if getter:
                        error_data = getter(response, error_data)
                        setattr(error_res, field, getter(response, error_data))
        if error_res:
            return error_res
        elif error_data:        
            return self.error_model(**error_data)
        else:
            None

    @staticmethod
    def handle_exception(exc, context) -> Response:
        # WARNING: Don't remove the default handler as it performs DB rollback and init headers
        self = ErrorHandler()
        response = drf_exception_handler(exc, context)
        self.error_model = self.get_error_model(view = context['view'])
        assert self.error_model, "Error model must be set"
        assert issubclass(self.error_model, JSONModel), "error_model must be an extension to JSONModel"
        
        try:
            error_res = self._handle(exc, context, response)
            if error_res:
                response.data = error_res.to_dict()
                if getattr(exc, 'headers', None):
                    response.headers.update(exc.headers)
                return response
        except:
            #TODO capture traceback and log this error, then send it to sentry/PROMETHEOUS
            print(response)
            import traceback
            traceback.print_exc()
            response.status_code = 500
            response.data = {
                'code': 'Error in handling error',
                'details': 'An unexpected error occurred during handling an error.'
            }
            return response
