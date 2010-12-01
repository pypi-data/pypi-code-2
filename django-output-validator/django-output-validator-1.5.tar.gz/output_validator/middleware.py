from output_validator.models import ValidationFailure


class ValidatorMiddleware(object):
    def process_response(self, request, response):
        if response.status_code == 200:
            ValidationFailure.do_validation(request, response)
        return response
