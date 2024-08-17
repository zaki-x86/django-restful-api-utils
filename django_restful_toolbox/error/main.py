from django_restful_toolbox.json_model import JSONModel, JSONField, BooleanField, StringField

__all__ = ['ErrorField', 'RestfulError']

class ErrorField(JSONField):
    code = StringField()
    details = StringField()    

class RestfulError(JSONModel):
    status = BooleanField(default=False)
    message = StringField(default='Error')
    error = ErrorField()
    this = StringField(default=None)
