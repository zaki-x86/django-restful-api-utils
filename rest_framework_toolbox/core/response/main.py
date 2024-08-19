from ..json_model import JSONModel, BooleanField, StringField, ListField


__all__ = ['RestfulResponse', 'RestfulError']

class RestfulResponse(JSONModel):
    class Data(JSONModel):
        pass
    status = BooleanField(default=True)
    message = StringField(default='')
    data = Data(default=None)
    this = StringField(default=None)
    links = ListField(default=None)


class RestfulError(JSONModel):
    class ErrorField(JSONModel):
        code = StringField()
        details = StringField()    
    status = BooleanField(default=False)
    message = StringField(default='Error')
    error = ErrorField()
    this = StringField(default=None)
