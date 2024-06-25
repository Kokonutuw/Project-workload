from django.core.validators import RegexValidator
from django.db import models


class Epic(models.Model):
    key_id = models.FloatField(verbose_name='Key id', null=True)
    date_update = models.DateField(verbose_name='Update date', auto_now=True)
    issue_key = models.CharField(verbose_name='Key', max_length=20)
    summary = models.CharField(verbose_name='Summary', max_length=2000, null=True)
    estimation = models.FloatField(verbose_name='Estimation', default=0)
    estimation_remaining = models.FloatField(verbose_name='Remaining', default=0)
    start_date=models.DateField(verbose_name='Start Date',null=True)
    end_date=models.DateField(verbose_name='End Date',null=True)
    color_regex=RegexValidator(regex="^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$")
    color=models.CharField(verbose_name='Color',null=True,max_length=7,default='#ffffff',validators=[color_regex])

    def __str__(self):
        epic_detail = '{} - {}'.format(self.issue_key,
                                       self.summary)
        return epic_detail
