from rest_framework_toolbox.core.json_model import (
    IntegerField,
    StringField,
    BooleanField,
    ListField,
    JSONModel,
)
import sys

class TestJSONModel:
    class BasicResponse(JSONModel):
        class Data(JSONModel):
            name = StringField(default='default')
            age = IntegerField(default=0)
        
        code = IntegerField()
        success = BooleanField()
        message = StringField()
        data = Data()
        links = ListField()
        
    class RandomData(JSONModel):
        pass

    def __init__(self):
        self.successfull_response = self.BasicResponse(
            code=200,
            success=True,
            message="OK",
            links=["https://example.com"],
        )
        self.inspect()
        self.successfull_response.data.name = "John Doe"
        self.successfull_response.data.age = 17
        #self.successfull_response.data.name = "John Doe"
        #self.successfull_response.data.age = 17
    
    def inspect(self):
        print("================ Inspection of class meta data ====================")
        print(self.successfull_response._fields.items())
        print("================ End inspection of class meta data ====================")
    
    def test_fields(self):
        assert self.successfull_response.code == 200
        assert self.successfull_response.success == True
        assert self.successfull_response.message == "OK"
        assert self.successfull_response.data.name == "John Doe", f'self.successfull_response.data.name = {self.successfull_response.data.name}'
        assert self.successfull_response.data.age == 17
        assert self.successfull_response.data.to_dict() == {"name": "John Doe", "age": 17}, f"error, self.successfull_response.data.to_dict() returned \n{self.successfull_response.data.to_dict()}"
        assert self.successfull_response.links == ["https://example.com"]
        assert self.successfull_response.to_dict() == {
            "code": 200,
            "success": True,
            "message": "OK",
            "data": {"name": "John Doe", "age": 17},
            "links": ["https://example.com"]
        }, f'successful_response.to_dict(), returned:\n{self.successfull_response.to_dict()}' 
        print("Test fields .. OK")
    
if __name__ == '__main__':
    test = TestJSONModel()
    test.test_fields()