from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.apps import apps  # ✅ Important

@receiver(post_save, sender=User)
def create_user_preference(sender, instance, created, **kwargs):
    if created:
        UserPreference = apps.get_model('users', 'UserPreference')  # ✅ No direct import
        UserPreference.objects.create(user=instance)
