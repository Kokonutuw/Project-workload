from django.db import models


class Versions(models.Model):
    date_update = models.DateTimeField(verbose_name='Update date', auto_now=True)
    name = models.CharField(verbose_name='Name', max_length=250)
    first_sprint = models.CharField(verbose_name='First Sprint', max_length=250, default='None', blank=True)
    last_sprint = models.CharField(verbose_name='Last Sprint', max_length=250, default='None', blank=True)
    start_date_dev = models.DateField(verbose_name='Start Dev', blank=True, null=True)
    end_date_dev = models.DateField(verbose_name='End Dev', blank=True, null=True)
    start_date_qa = models.DateField(verbose_name='Start QA', blank=True, null=True)
    end_date_qa = models.DateField(verbose_name='End QA', blank=True, null=True)
    stories = models.IntegerField(verbose_name='Stories', default=0)
    bugs = models.IntegerField(verbose_name='Bugs', default=0)
    estimation = models.FloatField(verbose_name='Estimation', default=0)
    estimation_remaining = models.FloatField(verbose_name='Remaining', default=0)
    deployment_date = models.DateField(verbose_name='Deployment', blank=True, null=True)

    def __str__(self):
        version_details = '{}'.format(self.name)
        return version_details
