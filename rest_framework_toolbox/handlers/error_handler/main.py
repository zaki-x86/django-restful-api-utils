from typing import Any, Dict, TypeVar, Callable

from ._config import configs

__testing = configs['test']

if not __testing:
    from rest_framework.exceptions import APIException
    from rest_framework.response import Response
    from rest_framework.views import exception_handler as drf_exception_handler
    from django.conf import settings
    
from rest_framework_toolbox.core.utils import import_class, get_class_fields, camel_to_snake
from rest_framework_toolbox.core.models import JSONModel


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
        'Http404'
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
        
    def _convert_to_apiexception(self, exc):
        pass
    
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
        view = context.get('view', None)
        exception_class = exc.__class__.__name__
        error_res = None
                
        assert view, "View is required to handle exceptions"
        assert self.error_model, "Error model is required to handle exceptions"
        
        # 1. Check if the user registered any custom handler against the exception 
        if exception_class in self._user_handlers:
            user_handler = self._user_handlers[exception_class]
            # User handler must return an instance of self.error_model class
            error_res = user_handler(exc, context, response)
            assert isinstance(error_res, self.error_model), "User-defined handler must return an instance of the error model"

            return error_res
        
        # 2. Check if the exception can be handled by view's 'on_error' method
        if getattr(view, 'on_error', None):
            serializer_error_handler = getattr(view, 'on_error', None)
            if serializer_error_handler and callable(serializer_error_handler):
                if isinstance(exc, APIException):
                    error_res = serializer_error_handler(exc, context, response)
                else:
                    pass
            if error_res:
                assert isinstance(error_res, self.error_model), "User-defined handler must return an instance of the error model"
                
                return error_res
        
        # 3. Fallback to default handlers defined in error_res if no `on_error` is defined
        elif exception_class in self._default_handlers:
            #print("Handling default exception")
            error_res = self.error_model()
            
            # Handle default exception using handler defined in error_res
            if getattr(error_res, camel_to_snake(exception_class), None):
                handler = getattr(error_res, camel_to_snake(exception_class), None)
                if callable(handler):
                    error_res = handler(context['request'], response)
                    if error_res:
                        assert isinstance(error_res, self.error_model), "User-defined handler must return an instance of the error model"
                        return error_res
        
        # 3. If no handler is defined, handle the error using the exception class user supplied attributes    
        else:
            error_response_fields = self._get_error_model_fields()
            error_res = self.error_model()

            for field in error_response_fields:
                # Check if the field value is set directly in the exc class
                if getattr(exc, field, None):
                    val = getattr(exc, field, None)
                    if val and callable(val):
                        val = val(context, exc.get_full_details())
                    setattr(error_res, field, val)

        # 4. Postprocessing
        if error_res:
            return error_res
        else:
            raise Exception(f"Error could not be handled:\n{exc.get_full_details()}")

    @staticmethod
    def handle_exception(exc, context) -> Response:
        print(f"Handling exception: {exc.__class__.__name__}")
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
