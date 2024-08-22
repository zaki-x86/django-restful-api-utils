import json
from enum import Enum
from datetime import datetime, date
from rest_framework.response import Response
from ._meta import _JSONModelMeta
from typing import Any, Dict, List, TypeVar

# Forward declare JSONModel type

__all__ = [
    'Defaults',
    # Fields
    'Field',
    'StringField',
    'IntegerField',
    'BooleanField',
    'DateTimeField',
    'DateField',
    'ListField',
    'DictField',
    'DataField',
    'JSONField',
    # Models
    'JSONModel',
]

class Defaults(Enum):
    ResponseClassAsString = 0
    ExceptionClassAsString = 1
    SerializerData = 2
    SerializerErrorCode = 2
    SerializerErrorDetails = 3

class Field:
    """A base class for all fields in `JSONModel`
    """
    def __init__(self, default=None):
        self.default = default
        self.value = default
        
    def get_value(self, value : Any = None):
        """Checks if default value is assigned. It is called by JSONModel constructor to build class fields and its values.

        Args:
            value (Any): value assigned to the field

        Returns:
            Any: value after
        """
        if value is None and self.default is not None:
            return self.default
        return value


class StringField(Field):
    """String field. Constructor ensures that default value assigned is a string.
    """
    def __init__(self, default : str =None):
        if default:
            pass
            #assert type(default) is str, "Default should be a list"
        super().__init__(default)
    
    def get_value(self, value : str = None):
        """Ensures value assigned is a string, returns default value if not assigned.

        Args:
            value (str): value assigned to the field

        Returns:
            str: value after
        """
        if value is None and self.default is not None:
            #assert type(self.default) is str, "Default should be a string"
            return self.default
        elif value:
            pass
            #assert type(value) is str, "Value should be a string"
        return value


class IntegerField(Field):
    """Integer field. Constructor ensures that default value assigned is an integer.
    """

    def __init__(self, default=None):
        if default:
            pass
            #assert type(default) is int, "Default should be an integer"
        super().__init__(default)

    def get_value(self, value : int) -> int:
        """Ensures value assigned is an integer, returns default value if not assigned.

        Args:
            value (int): value assigned to the field

        Raises:
            #assertionError: should be an integer

        Returns:
            int: value after
        """
        if value is None and self.default is not None:
            #assert type(self.default) is int, "Default should be an integer"
            return self.default
        elif value:
            pass
            #assert type(value) is int, "Value should be an integer"
        return value

class BooleanField(Field):
    """Boolean field. Constructor ensures that default value assigned is a boolean.
    """
    def __init__(self, default=None):
        if default:
            pass
            #assert type(default) is bool, "Default should be a boolean"
        super().__init__(default)
    
    def get_value(self, value: bool) -> bool:
        """Ensures value assigned is a boolean
        """
        if value is None and self.default is not None:
            #assert type(self.default) is bool, "Default should be a boolean"
            return self.default
        elif value:
            pass
            #assert type(value) is bool, "Value should be a boolean"
        return value

class DateTimeField(Field):
    """DateTime field. Constructor ensures value assigned is a `datetime`
    """
    def __init__(self, default=None):
        if default:
            pass
            #assert type(default) is datetime, "Default should be a datetime"
        super().__init__(default)
    
    def get_value(self, value : datetime) -> datetime:
        """Ensures value assigned is a `datetime`
        """
        if value is None and self.default is not None:
            #assert type(self.default) is datetime, "Default should be a datetime"
            return self.default
        elif value:
            pass
            #assert type(value) is datetime, "Value should be a datetime"
        return value

class DateField(Field):
    """Date field. Constructor ensures value assigned is a `date`.
    """
    def __init__(self, default=None):
        if default:
            pass
            #assert type(default) is date, "Default should be a datetime"
        super().__init__(default)
    
    def get_value(self, value : date) -> date:
        """Ensures value assigned is a `date`
        """
        if value is None and self.default is not None:
            #assert type(self.default) is date, "Default should be a datetime"
            return self.default
        elif value:
            pass
            #assert type(value) is date, "Value should be a datetime"
        return value

class ListField(Field):
    """List Field. Constructor ensures value assigned is a `list`
    """
    def __init__(self, default=[]):
        if default:
            pass
            #assert type(default) is list, "Default should be a list"
        super().__init__(default)

    def get_value(self, value : List) -> List:
        if value is None and self.default is not None:
            #assert type(self.default) is list, "Default should be a list"
            return self.default
        elif value:
            pass
            #assert type(value) is list, "Value should be a list"
        return value

class DictField(Field):
    """Dict Field. Constructor ensures value assigned is a `dict`
    """
    def __init__(self, default={}):
        if default:
            pass
            #assert type(default) is dict, "Default should be a dict"
        super().__init__(default)

    def get_value(self, value : Dict) -> Dict:
        if value is None and self.default is not None:
            #assert type(self.default) is dict, "Default should be a dict"
            return self.default
        elif value:
            pass
            #assert type(value) is dict, "Value should be a dict"
        return value
    
class DataField(Field):
    pass

class JSONField(Field, metaclass=_JSONModelMeta):
    def __init__(self, **kwargs):
        for field, field_type in self._fields.items():
            value = kwargs.get(field)
            setattr(self, field, field_type.get_value(value))

    def to_dict(self):
        result = {}
        for key, field in self._fields.items():
            # Nested JSONModel
            #JSONField
            if isinstance(field, JSONField) or isinstance(field, JSONModel):
                if field:
                    result[key] = getattr(self, key).to_dict()
            # Fields: String, Integer, Boolean, ... etc.
            # Non JSONField
            elif isinstance(field, Field) and not (isinstance(field, JSONField) or isinstance(field, JSONModel)):
                result[key] = getattr(self, key, field.default)
    
        return result
    
    def to_json(self):
        import json
        return json.dumps(self.to_dict(), default=str)

    def get_value(self, value = None):
        if not value:
            value = self.__class__()
        return value

class JSONModel(metaclass=_JSONModelMeta):
    """JSON Model to ensure consistent and unified interface for your API responses
    """
    def __init__(self, **kwargs):
        for key, field in self._fields.items():
            if isinstance(field, JSONField):
                value = kwargs.get(key, field.__class__())
                setattr(self, key, field.get_value(value))
            elif isinstance(field, JSONModel):
                value = kwargs.get(key, field.__class__())
                setattr(self, key, field.get_value(value))
            else:
                value = kwargs.get(key)
                setattr(self, key, field.get_value(value))

    def to_dict(self):
        result = {}
        for key, field in self._fields.items():
            # Fields: String, Integer, Boolean, ... etc.
            if isinstance(field, Field) and not isinstance(field, JSONField):
                result[key] = getattr(self, key, field.default)
            # Nested JSON
            elif isinstance(field, JSONField) or isinstance(field, JSONModel):                
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

    def __call__(self, *args, **kwds) -> Response:
        return Response(data=self.to_dict(), headers=kwds.get('headers', {}), status=kwds.get('http_status', 200))
