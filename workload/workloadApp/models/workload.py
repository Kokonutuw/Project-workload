from django.db import models
from ..models.personnes import Personnes


class Workload(models.Model):
    date_update = models.DateTimeField(verbose_name='Update datetime', auto_now=True)
    month = models.IntegerField(verbose_name='Month', null=True)
    year = models.IntegerField(verbose_name='Year', null=True)
    workload = models.FloatField(verbose_name='Workload', default=0)
    done_workload = models.FloatField(verbose_name='Done', default=0)
    personne_workload = models.ForeignKey(Personnes, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        workload_details = '{} - {} - {} - {} - {}'.format(self.personne_workload,
                                                           self.year, self.month, self.workload, self.done_workload)
        return workload_details
