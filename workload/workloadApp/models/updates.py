from django.db import models


class Updates(models.Model):
    date_update = models.DateTimeField(verbose_name='Update date', auto_now=True)
    tasks_date_update = models.DateField(verbose_name='Update date tasks', auto_now=True)
    projects_date_update = models.DateField(verbose_name='Update date projects', auto_now=True)
    last_cmd = models.CharField(verbose_name='Commande', max_length=250, default='')

    def __str__(self):
        update_details = '{} - {}'.format(self.tasks_date_update, self.projects_date_update)
        return update_details
