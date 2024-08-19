class _JSONModelMeta(type):
    def __new__(cls, name, bases, attrs):
        """Meta class for JSONModel and JSONField

        Args:
            name (str): name of the current class being init (it doesn't have to be a direct child class of metaclass)
            bases (list): all bases of the current class being init (meta is not included)
            attrs (dict): all current attributes of the class being init
        """
        fields = {}
        from .main import Field
        for key, value in attrs.items():
            if isinstance(value, Field) or isinstance(value, bases):
                fields[key] = value
                
        attrs['_fields'] = fields
        return super(_JSONModelMeta, cls).__new__(cls, name, bases, attrs)