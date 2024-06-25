from django.db import models


class Stories_epic(models.Model):
    date_update = models.DateField(verbose_name='Update date', auto_now=True)
    key = models.CharField(verbose_name='Key', max_length=20)
    summary = models.CharField(verbose_name='Summary', max_length=2000)
    status = models.CharField(verbose_name='Status', null=True, max_length=50)
    type = models.CharField(verbose_name='Type', null=True, max_length=50)
    epic = models.CharField(verbose_name='Epic', null=True, max_length=60)
    estimate_fs = models.FloatField(null=True, default=0)
    parent_key = models.CharField(verbose_name='Parent key', null=True, max_length=20)

    def __str__(self):
        story_details = '{} - {}'.format(
            self.key, self.summary)
        return story_details
