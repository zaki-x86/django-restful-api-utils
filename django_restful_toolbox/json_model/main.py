import json
from enum import Enum

from rest_framework.response import Response


__all__ = [
    'Defaults',
    'Field',
    'StringField',
    'IntegerField',
    'BooleanField',
    'DateTimeField',
    'JSONField',
    'ListField',
    'JSONModel',
]

class Defaults(Enum):
    ResponseClassAsString = 0
    ExceptionClassAsString = 1
    SerializerData = 2
    SerializerErrorCode = 2
    SerializerErrorDetails = 3
    
class Field:
    def __init__(self, default=None):
        #self.required = required
        self.default = default

    def get_value(self, value):
        if value is None and self.default is not None:
            return self.default
        # disabled checking if type is required
        #if value is None and self.required:
        #    raise ValueError("This field is required.")
        return value


class StringField(Field):
    pass


class IntegerField(Field):
    pass


class BooleanField(Field):
    pass


class DateTimeField(Field):
    pass


class JSONFieldMeta(type):
    def __new__(cls, name, bases, attrs):
        fields = {}
        for key, value in attrs.items():
            if isinstance(value, Field):
                fields[key] = value
        
        # Append all Response attributes to fields
        #for key, value in Response.__dict__.items():
        #    if isinstance(value, Field):
        #        fields[key] = value
                
        attrs['_fields'] = fields
        return super(JSONFieldMeta, cls).__new__(cls, name, bases, attrs)

class JSONField(Field, metaclass=JSONFieldMeta):
    def __init__(self, **kwargs):
        super().__init__(kwargs.get('default', None))
        for key, field in self._fields.items():
            value = kwargs.get(key, None)
            setattr(self, key, field.get_value(value))

    def get_value(self, value):
        if value is None and self.default is not None:
            return self.default

        result = {}
        for key, field in value._fields.items():
            result[key] = getattr(value, key, field.default)
        return result


class ListField(Field):
    pass


class JSONModelMeta(type):
    def __new__(cls, name, bases, attrs):
        fields = {}
        for key, value in attrs.items():
            if isinstance(value, Field):
                fields[key] = value
        
        # Append all Response attributes to fields
        #for key, value in Response.__dict__.items():
        #    if isinstance(value, Field):
        #        fields[key] = value
                
        attrs['_fields'] = fields
        return super(JSONModelMeta, cls).__new__(cls, name, bases, attrs)


class JSONModel(metaclass=JSONModelMeta):
    def __init__(self, **kwargs):
        for key, field in self._fields.items():
            value = kwargs.get(key, None)
            setattr(self, key, field.get_value(value))  

    def to_dict(self):
        result = {}
        for key, field in self._fields.items():
            result[key] = getattr(self, key, field.default)
        return result

    def to_json(self):
        import json
        return json.dumps(self.to_dict(), default=str)

    def __call__(self, *args, **kwds) -> Response:
        return Response(self.to_dict(), headers=kwds.get('headers', {}), status=kwds.get('http_status', 200))
    
    @staticmethod
    def self_link(request, *args, **kwds):
        return {
            'href': request.build_absolute_uri()
        }
