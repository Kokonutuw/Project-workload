from ..models.personnes import Personnes
from django.db import models


class Availability(models.Model):
    date_update = models.DateTimeField(verbose_name='Update datetime', auto_now=True)
    month = models.IntegerField(verbose_name='Month', null=True)
    year = models.IntegerField(verbose_name='Year', null=True)
    availability = models.FloatField(verbose_name='Availability', default=0)
    total_availability = models.FloatField(verbose_name='Total', default=0)
    personne_availability = models.ForeignKey(Personnes, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        availability_details = '{} - {} - {} - {} - {}'.format(self.personne_availability,
                                                               self.year, self.month, self.availability,
                                                               self.total_availability)
        return availability_details
