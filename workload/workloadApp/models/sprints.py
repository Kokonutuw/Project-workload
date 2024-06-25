from django.db import models


class Sprints(models.Model):
    date_update = models.DateTimeField(verbose_name='Update date', auto_now=True)
    name = models.CharField(verbose_name='Name', max_length=250)
    start_date = models.DateField(verbose_name='Start at', blank=True, null=True)
    end_date = models.DateField(verbose_name='End at', blank=True, null=True)
    estimation = models.FloatField(verbose_name='Estimation', default=0)
    estimation_remaining = models.FloatField(verbose_name='Remaining', default=0)
    resources_types = models.CharField(verbose_name='Resources', blank=True, null=True, max_length=500)

    def __str__(self):
        sprint = '{}'.format(self.name)
        return sprint
