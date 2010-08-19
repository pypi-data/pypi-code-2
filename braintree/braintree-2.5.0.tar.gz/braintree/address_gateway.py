import re
import braintree
from braintree.address import Address
from braintree.error_result import ErrorResult
from braintree.exceptions.not_found_error import NotFoundError
from braintree.resource import Resource
from braintree.successful_result import SuccessfulResult

class AddressGateway(object):
    def __init__(self, gateway):
        self.gateway = gateway
        self.config = gateway.config

    def create(self, params={}):
        Resource.verify_keys(params, Address.create_signature())
        if not "customer_id" in params:
            raise KeyError("customer_id must be provided")
        if not re.search("\A[0-9A-Za-z_-]+\Z", params["customer_id"]):
            raise KeyError("customer_id contains invalid characters")

        response = self.config.http().post("/customers/" + params.pop("customer_id") + "/addresses", {"address": params})
        if "address" in response:
            return SuccessfulResult({"address": Address(self.gateway, response["address"])})
        elif "api_error_response" in response:
            return ErrorResult(self.gateway, response["api_error_response"])

    def delete(self, customer_id, address_id):
        self.config.http().delete("/customers/" + customer_id + "/addresses/" + address_id)
        return SuccessfulResult()

    def find(self, customer_id, address_id):
        try:
            response = self.config.http().get("/customers/" + customer_id + "/addresses/" + address_id)
            return Address(self.gateway, response["address"])
        except NotFoundError:
            raise NotFoundError("address for customer " + customer_id + " with id " + address_id + " not found")

    def update(self, customer_id, address_id, params={}):
        Resource.verify_keys(params, Address.update_signature())
        response = self.config.http().put(
            "/customers/" + customer_id + "/addresses/" + address_id,
            {"address": params}
        )
        if "address" in response:
            return SuccessfulResult({"address": Address(self.gateway, response["address"])})
        elif "api_error_response" in response:
            return ErrorResult(self.gateway, response["api_error_response"])

