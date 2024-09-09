from typing import Any, List, Dict
from datetime import datetime, date
from rest_framework import serializers

# Forward declare JSONModel type

__all__ = [
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
    'ErrorField',
]

class Field:
    """A base class for all fields in `JSONModel`
    """
    def __init__(self, default=None):
        self.default = default
        self.allow_null = True
        self.read_only = False
        self.required = False
        self.help_text = ""
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
    
    def serializer(self, value = None):
        if value:
            return serializers.Field(
                default = value,
                allow_null = self.allow_null,
                read_only = self.read_only,
                required = self.required
            )
        return serializers.Field(
            default = self.default,
            allow_null = self.allow_null,
            read_only = self.read_only,
            required = self.required
        )    
        
    def __repr__(self):
        return f"<{self.__class__}>: {self.value}"


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

    def serializer(self, value = None):
        if value:
            return serializers.CharField(
                default = value,
                allow_null = self.allow_null,
                read_only = self.read_only,
                required = self.required,
            )
        return serializers.CharField(
            default = self.default,
            allow_null = self.allow_null,
            read_only = self.read_only,
            required = self.required
        )

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

    def serializer(self, value = None):
        if value:
            return serializers.IntegerField(
                default = value,
                allow_null = self.allow_null,
                read_only = self.read_only,
                required = self.required
            )
        return serializers.IntegerField(
            default = self.default,
            allow_null = self.allow_null,
            read_only = self.read_only,
            required = self.required
        )
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
    
    def serializer(self, value = None):
        if value:
            return serializers.BooleanField(
                default = value,
                allow_null = self.allow_null,
                read_only = self.read_only,
                required = self.required
            )
        return serializers.BooleanField(
            default = self.default,
            allow_null = self.allow_null,
            read_only = self.read_only,
            required = self.required
        )

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
    
    def serializer(self, value = None):
        if value:
            return serializers.DateTimeField(
                default = value,
                allow_null = self.allow_null,
                read_only = self.read_only,
                required = self.required
            )
        return serializers.DateTimeField(
            default = self.default,
            allow_null = self.allow_null,
            read_only = self.read_only,
            required = self.required
        )

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

    def serializer(self, value = None):
        if value:
            return serializers.DateField(
                default = value,
                allow_null = self.allow_null,
                read_only = self.read_only,
                required = self.required
            )
        return serializers.DateField(
            default = self.default,
            allow_null = self.allow_null,
            read_only = self.read_only,
            required = self.required
        )
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

    def serializer(self, value = None):
        if value:
            return serializers.ListField(
                default = value,
                allow_null = self.allow_null,
                read_only = self.read_only,
                required = self.required
            )
        return serializers.ListField(
            default = self.default,
            allow_null = self.allow_null,
            read_only = self.read_only,
            required = self.required
        )

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
    
    def serializer(self, value= None):
        if value:
            
            return serializers.DictField(
                default = value,
                allow_null = self.allow_null,
                read_only = self.read_only,
                required = self.required
            )
        return serializers.DictField(
            default = self.default,
            allow_null = self.allow_null,
            read_only = self.read_only,
            required = self.required
        )
class DataField(Field):
    def serializer(self, custom_serializer):
        if isinstance(custom_serializer, serializers.Field):
            return custom_serializer
        
        return custom_serializer(
            default = self.default,
            allow_null = self.allow_null,
            read_only = self.read_only,
            required = self.required
        )
