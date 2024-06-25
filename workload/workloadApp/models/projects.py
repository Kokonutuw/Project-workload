from django.db import models


class Projects(models.Model):
    date_update = models.DateTimeField(verbose_name='Update datetime', auto_now=True)
    key = models.CharField(verbose_name='Key', max_length=20)
    name = models.CharField(verbose_name='Name', max_length=2000)
    category = models.CharField(verbose_name='Category', max_length=2000)
    tasks = models.IntegerField(default=0)
    stories = models.IntegerField(default=0)
    bugs = models.IntegerField(default=0)
    tasks_done = models.IntegerField(default=0)
    stories_done = models.IntegerField(default=0)
    bugs_done = models.IntegerField(default=0)
    lead = models.CharField(verbose_name='Project Lead', max_length=50, default='')

    def __str__(self):
        project_details = '{} - {} - {} - {}'.format(self.key,
                                                     self.name, self.category, self.lead)
        return project_details
