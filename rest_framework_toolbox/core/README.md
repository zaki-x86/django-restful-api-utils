# Core

The core library provides the following facilities:

## Fields

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


### The `DataField`

The data field is a special field as it is normally used as a placeholder when the data type of the field is not particular known.

It is useful when you want to populate this field with serializer data or serializer errors, or even a custom response of your own which could be a string, a list, or anything else.

## Models: `JSONModel`

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