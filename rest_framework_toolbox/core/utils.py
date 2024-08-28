from typing import Any

def import_class(module_path: str) -> Any:
    module_name, class_name = module_path.rsplit('.', 1)
    from importlib import import_module
    module = import_module(module_name)
    return getattr(module, class_name, None)

def get_class_name(obj):
    return obj.__class__.__name__

def get_class_fields(_class):
    return [attr for attr in dir(_class) if not callable(getattr(_class, attr)) and not attr.startswith("__") and not attr.startswith("_")]


def camel_to_snake(name):
    import re
    # Find all uppercase letters and add an underscore before them
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    # Convert the entire string to lowercase
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
