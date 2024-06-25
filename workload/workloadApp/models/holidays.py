from django.db import models

from ..models.personnes import Personnes


class Holidays(models.Model):
    start_date = models.DateField(verbose_name='Start date', null=True)
    end_date = models.DateField(verbose_name='End date', null=True)
    date_update = models.DateTimeField(verbose_name='Update datetime', auto_now=True)
    duration = models.FloatField(verbose_name='Duration', default=0)
    person_holidays = models.ForeignKey(Personnes, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        holidays_details = '{} - {} - {} - {}'.format(self.person_holidays,
                                                      self.start_date, self.end_date, self.duration)
        return holidays_details
