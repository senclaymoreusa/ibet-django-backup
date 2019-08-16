from django.forms import ModelForm
from .models import Notification

class PostNotificationForm(ModelForm):
    class Meta:
        model = Notification
        fields = ['subject', 'content_text', 'notifiers']