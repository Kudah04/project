from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Images
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

@receiver(post_save, sender=Images)
def image_saved(sender, instance, **kwargs):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'notifications', 
        {
            'type': 'image_notification',
            'message': 'A new image has been uploaded!',
        }
    )
