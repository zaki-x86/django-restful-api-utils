from django_restful_toolbox.json_model import JSONModel, BooleanField, StringField, JSONField


__all__ = ['RestfulResponse']

class RestfulResponse(JSONModel):
    status = BooleanField(default=True)
    message = StringField(default='')
    data = JSONField(default=None)
    this = StringField(default=None)
    links = JSONField(default=None)
