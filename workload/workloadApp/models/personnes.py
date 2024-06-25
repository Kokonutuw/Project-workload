from django.db import models


class Personnes(models.Model):
    date_update = models.DateTimeField(verbose_name='Update datetime', auto_now=True)
    name = models.CharField(verbose_name='Jira Name', max_length=50)
    last_name = models.CharField(verbose_name='Last name', max_length=50, default='')
    first_name = models.CharField(verbose_name='First Name', max_length=50, default='')
    email = models.CharField(verbose_name='Email', max_length=2000)
    resource_type = models.CharField(verbose_name='Resource Type', max_length=50, default='')

    def __str__(self):
        personnes_details = '{} - {} - {}'.format(self.name,
                                                  self.email, self.resource_type)
        return personnes_details

    def __eq__(self, other):
        return self.name == other.name
