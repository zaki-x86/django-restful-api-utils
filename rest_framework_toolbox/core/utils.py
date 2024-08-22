from typing import Any

def import_class(module_path: str) -> Any:
    module_name, class_name = module_path.rsplit('.', 1)
    from importlib import import_module
    module = import_module(module_name)
    return getattr(module, class_name, None)

def get_class_name(obj):
    return obj.__class__.__name__
