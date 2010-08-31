import django.dispatch

# This signal is fired when the authentication process fails.
# You can override the standard error response by passing
# a new response to the override_response callable.
api_auth_challenge = django.dispatch.Signal(
    providing_args = ["override_response"])

# If the authentication is successful this signal allow you
# to set custom attributes in the request object that can be
# used in other places.
api_auth_success = django.dispatch.Signal(
    providing_args = ["request", "consumer_key"])

# This signal is fired when the authentication process fails.
# You can override the result of the authentication process by
# calling the override_consumer caller providing a consumer key.
api_auth_fail = django.dispatch.Signal(
    providing_args = ["request", "override_consumer"])
