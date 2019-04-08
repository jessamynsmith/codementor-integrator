from django.db import models
from django.contrib.postgres.fields import JSONField


class CodementorWebhook(models.Model):
    event_name = models.CharField(max_length=40)
    data = JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    # TODO How to know what user the data is for? Maybe require everyone to add a url parameter of their email?

    def __str__(self):
        return '{} ({})'.format(self.event_name, self.created_at)
