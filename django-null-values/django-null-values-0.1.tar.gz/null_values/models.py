from django.db.models.signals import pre_save
from django.dispatch import receiver

@receiver(pre_save)
def update_nulls(sender, instance, **kwargs):
    for field in instance._meta.fields:
        if field.null and getattr(instance, field.name) == "":
            setattr(instance, field.name, None)
