from django.db import models


class Stories(models.Model):
    date_update = models.DateField(verbose_name='Update date', auto_now=True)
    version = models.CharField(verbose_name='Version', max_length=2000)
    key = models.CharField(verbose_name='Key', max_length=20)
    summary = models.CharField(verbose_name='Summary', max_length=2000)
    sprint = models.CharField(verbose_name='Sprint', max_length=2000)
    assignee = models.CharField(verbose_name='Assignee', max_length=50)
    tasks_link = models.CharField(max_length=250)
    estimation = models.FloatField(default=0)
    estimation_done = models.FloatField(default=0)
    status = models.CharField(verbose_name='Status', null=True, max_length=50)
    type = models.CharField(verbose_name='Type', null=True, max_length=50)

    def __str__(self):
        story_details = '{} - {}'.format(
            self.key, self.summary)
        return story_details
