import django.dispatch

pre_push = django.dispatch.Signal(providing_args=["toppings", "size"])