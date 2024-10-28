import logging
from rest_framework.renderers import JSONRenderer
from django.conf import settings
from rest_framework_toolbox.core.utils import import_class

__all__ = [
    'RestJsonRenderer'
]

def get_response_class(view = None):
    from django.conf import settings
    from rest_framework_toolbox.core.utils import import_class
    
    if view and hasattr(view, 'success_model'):
        return view.success_model
    elif getattr(settings, 'SUCCESS_JSON_MODEL', None):
        return import_class(settings.SUCCESS_JSON_MODEL)
    else:
        raise Exception("Must define a view-based or global JSON response model")

class RestJsonRenderer(JSONRenderer):
    def __init__(self, *args, **kwargs):
        super(RestJsonRenderer, self).__init__(*args, **kwargs)
        logger_obj = getattr(settings, 'JSON_RENDERER_LOGGER', None)
        if logger_obj:
            self.logger = import_class(logger_obj)
        else:
            self.logger = logging.getLogger('rest_framework_toolbox')
        
    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = getattr(renderer_context['view'], 'response', None)
        view = renderer_context.get('view', None)
        request = renderer_context.get('request', None)
        get_success_response = getattr(view, 'on_success', None)
        
        # Leave error response alone as it is handled by exception handler
        if response.status_code >= 400:
            self.post_rendering_actions(view, request, response.status_code, data)
            return super(RestJsonRenderer, self).render(data, accepted_media_type, renderer_context)
        
        elif renderer_context and get_success_response:
            request =  renderer_context['view'].request
            response_data = get_success_response(request, data).to_dict()
            self.post_rendering_actions(view, request, response.status_code, data)
            return super(RestJsonRenderer, self).render(response_data, accepted_media_type, renderer_context)
        
        self.post_rendering_actions(view, request, response.status_code, data)
        return super(RestJsonRenderer, self).render(data, accepted_media_type, renderer_context)

    def post_rendering_actions(self, view, request, status_code, response):
        user = getattr(request, 'user', None)
        if user:
            id = user.id
        else:
            id = -1
        action = view.__class__.__name__
        path_info = request.path_info
        req_data = getattr(request, 'data', None)
        
        self.logger.info(f"User ID: {id} attempted {action} {path_info} {req_data} and system responded with status code {status_code} {response}")
    