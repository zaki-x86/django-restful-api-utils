from rest_framework_toolbox.core.response import (
    RestfulError,
    RestfulResponse
)


class TestResponses:
    def test_restful_response(self):
        response = RestfulResponse()
        assert response.status_code == 200
        assert response.data == {}

    def test_restful_error(self):
        error = RestfulError()
        assert error.status_code == 400
        assert error.data == {}