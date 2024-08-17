from rest_framework.renderers import JSONRenderer

__all__ = [
    'RestJsonRenderer'
]

class RestJsonRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        response_class = getattr(renderer_context['view'], 'response_class', None)
        request =  renderer_context['view'].request
                
        if response_class is None:
            return super(RestJsonRenderer, self).render(data, accepted_media_type, renderer_context)
        
        get_response_instance = getattr(response_class(), f'{request.method.lower()}', None)
        get_response_headers = getattr(response_class(), f'{request.method.lower()}_headers', None)
        
        if get_response_instance:
            response_data = get_response_instance(data, renderer_context).to_dict()
        else:
            response_data = data

        if get_response_headers:
            headers = get_response_headers(data, renderer_context)
            for key, value in headers.items():
                renderer_context['response'][key] = value

        return super(RestJsonRenderer, self).render(response_data, accepted_media_type, renderer_context)
