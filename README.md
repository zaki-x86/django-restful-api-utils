# Django Rest framework Toolbox

## Core

The core library provides the following facilities:

### Fields

The following fields are part of the core library:

- `Field`
- `StringField`
- `IntegerField`
- `BooleanField`
- `DateTimeField`
- `DateField`
- `ListField`
- `DictField`
- `DataField`

All fields implement the `Field` class.

the `Field::get_value` method returns the field value after performing validations on it.


#### The `DataField`

The data field is a special field as it is normally used as a placeholder when the data type of the field is not particular known.

It is useful when you want to populate this field with serializer data or serializer errors, or even a custom response of your own which could be a string, a list, or anything else.

### Models: `JSONModel`

This class is used to declare the structure of your responses so the renderer can be informed about it and generates a response JSON using its attributes.

Example:

```py
# responses/success.py
class SuccessResponse(JSONModel):
    status = BooleanField(default=True)
    message = StringField(default="Successful request")
    data = DataField(default=None)

# main.py
login_res = SuccessResponse(
    status = True,
    message = "Login Successful",
    data = "user logged in"
)
```

The `JSONModel` itself can be a field within a response JSON model:

```py
# responses/fail.py
class ErrorField(JSONModel):
    code = StringField()
    details = StringField()

class FailResponse(JSONModel):    
    status = BooleanField(default=False)
    message = StringField(default="Failed request")
    error = ErrorField()

# main.py
login_failed = FailResponse(
    status = False,
    message = "Login Failed",
    error = ErrorField(
        code = "validation_error",
        details = {
            "email": [
                "Invalid email"
            ]
        }
    )
)
```

## Handlers

The handlers package provides the following facilities:

- `ErrorHandler`
- `JSONModelRenderer`
- `Linker`

### How to use it?

#### Configuration

##### 1. Create response JSON schema for successful and failed responses

Create response classes that extends `JSONModel` for example:

```py
# common/responses.py
from rest_framework_toolbox.core.models import JSONModel
from rest_framework_toolbox.core.fields import BooleanField, StringField

class ErrorField(JSONModel):
    code = StringField()
    details = StringField()

class FailResponse(JSONModel):    
    status = BooleanField(default=False)
    message = StringField(default="Failed request")
    error = DataField()

class SuccessResponse(JSONModel):
    status = BooleanField(default= True)
    message = StringField(default="Successful request")
    data = DataField()
```

##### 2. Configure django settings

```py
# settings.py

# Introduce DRF to our handlers:

REST_FRAMEWORK = {
    ... ,
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework_toolbox.handlers.RestJsonRenderer',
    ),
    'EXCEPTION_HANDLER': 'rest_framework_toolbox.handlers.exception_handler',
}

# Tell the handlers where your schemas are 
ERROR_JSON_MODEL = "common.responses.FailResponse"
SUCCESS_JSON_MODEL = "common.responses.SuccessResponse"
```

#### Usage

Go to your view class and add these methods:

- `on_success`, and
- `on_error`

```py
class LoginView(APIView):
    ...

    def on_success(self, request, data):
        return SuccessResponse(
            status = True,
            message = 'Login successful',
            data = data,
        )
        
    def on_error(self, exc, context, response):
        error = ErrorField(
            code = exc.default_code,
            details = exc.detail
        )
        
        return FailResponse(
            status = False,
            message = "Authentication Failed",
            error = error
        )
```

##### `on_success`

The JSON renderer calls this method and provides you some context such as: `request`, `data`. The `data` object is the response data that gets returned from your view.

##### `on_error`

The exception handler calls this method and provides you with context data, such as:

- `exc`: the exception object that was raised, so you can customize your error response depending on what type of exception was thrown within your view.
- `context`: the context dictionary which contains:
    - `view`
    - view's `args`
    - view's `kwargs`
    - `request`
- `response` the response object, in case you may want to add any custom headers, or register post response callbacks.

- `on_error` must return an instance of the error model you defined in your settings, otherwise, the exception handler will fail.

### `JSONModelRenderer` in depth

The renderer ignores responses with status codes that are less than `400` so the exception handler can handle them.

If it found the method `on_success` in your view, it calls the method and provides it the context data.

In case if it didn't find `on_success` method in your view, it returns the response data as it is, ignoring your custom schema.

### `ErrorHandler` in depth

The `ErrorHandler` exposes the `exception_handler` function, so you can inform `rest_framework` to use it for handling exceptions.

It follows these steps to handle the thrown exception in your view:

1. It calls the default DRF handler.

This unavoidable as it performs any database rollbacks in case if the error thrown occurred during saving data.

The default handler can only handle exceptions that extends `APIException`, otherwise, an assertion error will be returned.

2. It starts looking for your defined errror JSON model in your settings, in case, if it is not found, an exception is returned by the handler that it can't find your error model.

3. It calls your `on_error` method.

#### Handling failures

The exception handler throws exceptions when it fails to handle the error and logs the error if debug is set to `True` in your settings, otherwise, it returns a `500` response:

```json
{
    "code": "Error in handling error",
    "details": "An unexpected error occurred during handling an error."
}
```

#### Define your custom exceptions

You can define your custom exception classes and you can handle them in `on_error` method, you can also introduce custom headers, or register post renderer callback in your exception class:

```py
class MyException(APIException):
    default_code = "my_exception"
    detail = "This is a detailed error message"
    headers = {
        "x-err": "my custom exception"
    }
    callback = post_renderer
```

#### Define fallback default handlers in case 'on_error` is not defined in your view or can't handle the thrown exception

Within your error JSON model class you can define default handlers, for example:

if the exception class thrown is `PermissionDenied`, then define its handler with the name `permission_denied`


```py
class FailResponse(JSONModel):    
    status = BooleanField(default=False)
    message = StringField(default="Failed request")
    error = ErrorField()

    # Define common errors handlers
    def permission_denied(self, request, response):
        return FailResponse(
            status = False,
            message = "You do not have permission to perform this action",
            error = ErrorField(
                code = "permission_denied",
                details = "You do not have permission to perform this action"
            )
        )
```

## Swagger

>> In Progress