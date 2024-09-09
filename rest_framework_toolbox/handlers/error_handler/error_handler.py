from rest_framework.views import exception_handler as drf_exception_handler
from django.conf import settings
from rest_framework_toolbox.core.utils import import_class
from rest_framework_toolbox.core.models import JSONModel
from .main import ErrorHandler

__all__ = [
    'exception_handler',
]

def get_error_model(view = None):
    if view and hasattr(view, 'error_model'):
        return view.error_model
    elif getattr(settings, 'ERROR_JSON_MODEL', None):
        return import_class(settings.ERROR_JSON_MODEL)
    else:
        raise Exception("A global error json model must be set")
    
def exception_handler(exc, context):
    # WARNING: Don't remove the default handler as it performs DB rollback
    response = drf_exception_handler(exc, context)
    assert response, "DRF Exception handler didn't return a response, this could be due to the exception thrown is not an instance of excpetions.APIException"
    try:
        error_model = get_error_model(view = context['view'])
        assert error_model, "Error JSON model not found"
        assert issubclass(error_model, JSONModel), f"error class: {error_model.__class__.__name__} must be an extension to JSONModel"
        
        handler = ErrorHandler(error_model=error_model)
        error_res = handler._handle(exc, context, response)
        assert error_res, "Error handler did not return a response"
        assert isinstance(error_res, error_model), f"handler response must be an instance of {settings.ERROR_JSON_MODEL}"
        
        response.data = error_res.to_dict()
        if getattr(exc, 'headers', None):
            response.headers.update(exc.headers)
        if getattr(exc, 'callback', None):
            response.add_post_render_callback(exc.callback)
        return response
        
    except Exception as e:
        #TODO capture traceback and log this error, then send it to sentry/dashboard
        import traceback
        traceback.print_exc()
        if settings.DEBUG:
            raise e
        else:
            response.status_code = 500
            response.data = {
                'code': 'Error in handling error',
                'details': 'An unexpected error occurred during handling an error.'
            }
            return response
