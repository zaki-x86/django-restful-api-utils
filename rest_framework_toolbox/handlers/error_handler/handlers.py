def _handler_parse_error(exc, context, res):
    return {
        'code': "parsing_error",
        'details': exc.get_full_details()
    }

def _handler_not_authenticated_error(exc, context, res):
    return {
        'code': "not_authenticated",
        'details': exc.get_full_details()
    }

def _handler_authentication_error(exc, context, res):
    return {
        'code': "authenticated_error",
        'details': exc.get_full_details()
    }
    
    return res

def _handler_invalid_token_error(exc, context, res):
    return {
        'code': "invalid_token",
        'details': exc.get_full_details()
    }
    
def _handler_validation_error(exc, context, res):
    return {
        'code': 'validation_error',
        'details': exc.get_full_details()
    }

def _handler_permission_denied_error(exc, context, res):
    return {
        'code': "permission_denied",
        'details': exc.get_full_details()
    }

def _handler_not_found_error(exc, context, res):
    return {
        'code': "not_found",
        'details': exc.get_full_details()
    }

def _handler_method_not_allowed_error(exc, context, res):
    return {
        'code': "method_not_allowed",
        'details': exc.get_full_details()
    }

def _handler_throttled_error(exc, context, res):
    return {
        'code': "throttled",
        'details': exc.get_full_details()
    }

def _handler_service_unavailable_error(exc, context, res):
    return {
        'code': "service_unavailable",
        'details': exc.get_full_details()
    }
