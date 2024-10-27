from rest_framework_toolbox.error_handler.main import GlobalErrorHandler
from rest_framework_toolbox.core.models import JSONModel, StringField, BooleanField


class ErrorModel(JSONModel):
    class Data(JSONModel):
        code = StringField()
        reason = StringField()
        
    status = BooleanField()
    message = StringField()
    data = Data()


def some_handler():
    return {
        'status': False,
        'message': 'some message',
        'data': {
            'code': 'some code',
            'reason': 'some reason'
        }
    }

if __name__ == "__main__":
    handler = GlobalErrorHandler(error_model = ErrorModel)
    fields = handler._get_error_model_fields()
    print(fields)
    # construct response
    res = {}
    error_data = some_handler()
    # populate error_data to their correspong field
    for field in fields:
        res[field] = error_data.get(field, None)
    
    