import uuid
from django.db import models


class Message(models.Model):
    msg_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    login = models.CharField(max_length=256)
    topic = models.CharField('topic', max_length=256)
    send_date = models.DateTimeField()
    receive_date = models.DateTimeField(auto_now_add=True)
    from_email = models.CharField(max_length=256)
    message_text = models.TextField()
    attachments = models.FileField(upload_to='attachments/', null=True, blank=True, max_length=300)
    email_server = models.CharField(max_length=30)


class User(models.Model):
    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)



