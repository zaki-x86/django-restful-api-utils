from enum import Enum
from rest_framework.response import Response
from ._meta import _JSONModelMeta
from ..fields import Field

# Forward declare JSONModel type

__all__ = [
    'Defaults',
    # Models
    'JSONModel',
]

class Defaults(Enum):
    ResponseClassAsString = 0
    ExceptionClassAsString = 1
    SerializerData = 2
    SerializerErrorCode = 2
    SerializerErrorDetails = 3

class JSONModel(metaclass=_JSONModelMeta):
    """JSON Model to ensure consistent and unified interface for your API responses
    """
    def __init__(self, **kwargs):
        for key, field in self._fields.items():
            if isinstance(field, JSONModel):
                value = kwargs.get(key, field.__class__())
                setattr(self, key, field.get_value(value))
            else:
                value = kwargs.get(key)
                setattr(self, key, field.get_value(value))

    def to_dict(self):
        """
        Generates a dictionary representation of the model
        :return: dict
        :rtype: dict
        """
        result = {}
        for key, field in self._fields.items():
            # Fields: String, Integer, Boolean, ... etc.
            if isinstance(field, Field):
                result[key] = getattr(self, key, field.default)
            # Nested JSON
            elif isinstance(field, JSONModel):                
                result[key] = getattr(self, key).to_dict()
            
        return result
    
    def set_value(self, name, val):
        setattr(self, name, val)        

    def to_json(self):
        import json
        return json.dumps(self.to_dict(), default=str)
    
    def get_value(self, value = None):
        if not value:
            value = self.__class__()
        return value

    def to_response(self, *args, **kwds):
        return Response(data=self.to_dict(), headers=kwds.get('headers', {}), status=kwds.get('http_status', 200))

    def serializer(self, *args, **kwds):
        serializer_fields = {}
        for key, field in self._fields.items():
            if isinstance(field, (Field, JSONModel)):
                serializer_fields[key] = field.serializer()
        
        from rest_framework import serializers
        return type(
            self.__class__.__name__ + 'Serializer',
            (serializers.Serializer,),
            serializer_fields
        )
        
            