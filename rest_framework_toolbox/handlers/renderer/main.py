from rest_framework.renderers import JSONRenderer

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
    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = getattr(renderer_context['view'], 'response', None)
        get_success_response = getattr(renderer_context['view'], 'on_success', None)
        
        # Leave error response alone as it is handled by exception handler
        if response.status_code >= 400:
            return super(RestJsonRenderer, self).render(data, accepted_media_type, renderer_context)
        
        elif renderer_context and get_success_response:
            request =  renderer_context['view'].request
            response_data = get_success_response(request, data).to_dict()

            return super(RestJsonRenderer, self).render(response_data, accepted_media_type, renderer_context)
        
        return super(RestJsonRenderer, self).render(data, accepted_media_type, renderer_context)
