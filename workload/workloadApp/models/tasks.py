from django.db import models


class Tasks(models.Model):
    date_update = models.DateField(verbose_name='Update date', auto_now=True)
    version = models.CharField(verbose_name='Version', max_length=2000)
    key = models.CharField(verbose_name='Key', max_length=20)
    summary = models.CharField(verbose_name='Summary', max_length=2000)
    sprint = models.CharField(verbose_name='Sprint', max_length=2000)
    assignee = models.CharField(verbose_name='Assignee', max_length=50)
    resource_type = models.CharField(verbose_name='Resource Type', max_length=50)
    story_link = models.CharField(max_length=20)
    estimation = models.FloatField(default=0)
    estimation_done = models.FloatField(default=0)
    status = models.CharField(verbose_name='Status', null=True, max_length=50)
    start_date = models.DateField(verbose_name='Start date', null=True)
    end_date = models.DateField(verbose_name='End date', null=True)

    def __str__(self):
        task_details = '{} - {} - {} - {} - {} - {} - {}'.format(self.version,
                                                                 self.key, self.summary, self.sprint, self.assignee,
                                                                 self.resource_type,
                                                                 self.story_link)
        return task_details
