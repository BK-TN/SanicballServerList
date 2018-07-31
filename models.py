from django.db import models

class ServerEntry(models.Model):
    ip = models.CharField('IP', max_length=128)
    port = models.IntegerField('Port')
    last_ping = models.DateTimeField("Last ping") # Used to remove servers after they don't respond for a while
