from rest_framework import serializers


class SchemaError(serializers.Serializer):
    class ErrorFieldSerializer(serializers.Serializer):
        code = serializers.CharField(default="<error_code>")
        details = serializers.DictField()

    def __init__(self, *args, **kwargs) -> None:
        self.status_code = kwargs.pop('status_code', 400)
        super().__init__(*args, **kwargs)

    status = serializers.BooleanField(default=False)
    message = serializers.CharField(default=None, allow_null=True)
    error = ErrorFieldSerializer()


class SchemaSuccess(serializers.Serializer):
    status = serializers.BooleanField(default=True)
    message = serializers.CharField(default=None, allow_null=True)
    data = serializers.DictField()
    links = serializers.DictField()


class PermissionDenied:
    def __init__(self, **kwargs) -> None:
        self.status_code = 403
        self.serializer = SchemaError(
            data = {
                'status': False,
                'message': kwargs.get('message', 'You do not have permission to perform this action.'),
                'error': {
                    'code': "permission_denied",
                    'details': kwargs.get('message', 'You do not have permission to perform this action.')
                }
            }
        )
        self.serializer.is_valid()

    def __call__(self):
        return self.serializer.data
    
class NotFound:
    def __init__(self, **kwargs) -> None:
        self.status_code=404
        self.serializer = SchemaError(
            data = {
                'status': False,
                'message': kwargs.get('message', 'The requested resource was not found.'),
                'error': {
                    'code': "not_found",
                    'details': kwargs.get('message', 'The requested resource was not found.')
                }
            }
        )
        self.serializer.is_valid()

    def __call__(self):
        return self.serializer.data

class ValidationError:
    def __init__(self, **kwargs) -> None:
        self.status_code=400
        self.serializer = SchemaError(
            data = {
                'status': False,
                'message': kwargs.get('message', 'Validation error'),
                'error': {
                    'code': "validation_error",
                    'details': kwargs.get('message', 'Validation error')
                }
            }
        )
        self.serializer.is_valid()

    def __call__(self):
        return self.serializer.data

class AuthenticationFailed:
    def __init__(self, **kwargs) -> None:
        self.status_code=401
        self.serializer = SchemaError(
            data = {
                'status': False,
                'message': kwargs.get('message', 'Authentication failed'),
                'error': {
                    'code': "authentication_failed",
                    'details': kwargs.get('message', 'Authentication failed')
                }
            }
        )
        self.serializer.is_valid()
    
    def __call__(self):
        return self.serializer.data
     
class NotAuthenticated():
    def __init__(self, **kwargs) -> None:
        self.status_code=401
        self.serializer = SchemaError(
            data = {
                'status': False,
                'message': kwargs.get('message', 'Not authenticated'),
                'error': {
                    'code': "not_authenticated",
                    'details': kwargs.get('message', 'Not authenticated')
                }
            }
        )
        self.serializer.is_valid()
        
    def __call__(self):
        return self.serializer.data


class MethodNotAllowed:
    def __init__(self, **kwargs) -> None:
        self.status_code=405
        self.serializer = SchemaError(
            data = {
                'status': False,
                'message': kwargs.get('message', 'Method not allowed'),
                'error': {
                    'code': "method_not_allowed",
                    'details': kwargs.get('message', 'Method not allowed')
                }
            }
        )
        self.serializer.is_valid()
        
    def __call__(self):
        return self.serializer.data


class NotAcceptable:
    def __init__(self, **kwargs) -> None:
        self.status_code=406
        self.serializer = SchemaError(
            data = {
                'status': False,
                'message': kwargs.get('message', 'Not acceptable'),
                'error': {
                    'code': "not_acceptable",
                    'details': kwargs.get('message', 'Not acceptable')
                }
            }
        )
        self.serializer.is_valid()
        
    def __call__(self):
        return self.serializer.data


class InvalidToken:
    def __init__(self, **kwargs) -> None:
        self.status_code=400
        self.serializer = SchemaError(
            data = {
                'status': False,
                'message': kwargs.get('message', 'Invalid token'),
                'error': {
                    'code': "invalid_token",
                    'details': kwargs.get('message', 'Invalid token')
                }
            }
        )
    
    def __call__(self):
        return self.serializer


class ParseError:
    def __init__(self, **kwargs) -> None:
        self.status_code=400
        self.serializer = SchemaError(
            data = {
                'status': False,
                'message': kwargs.get('message', 'Parse error'),
                'error': {
                    'code': "parse_error",
                    'details': kwargs.get('message', 'Parse error')
                }
            }
        )
        
    def __call__(self):
        return self.serializer


class Throttled:
    def __init__(self, **kwargs) -> None:
        self.status_code=429
        self.serializer = SchemaError(
            data = {
                'status': False,
                'message': kwargs.get('message', 'Request throttled'),
                'error': {
                    'code': "throttled",
                    'details': kwargs.get('message', 'Request throttled')
                }
            }
        )
        
    def __call__(self):
        return self.serializer


class ServiceUnavailable(SchemaError):
    def __init__(self, **kwargs) -> None:
        self.status_code=500
        self.serializer = SchemaError(
            data = {
                'status': False,
                'message': kwargs.get('message', 'Service unavailable'),
                'error': {
                    'code': "service_unavailable",
                    'details': kwargs.get('message', 'Service unavailable')
                }
            }
        )

    def __call__(self):
        return self.serializer