from django.forms import ModelForm

from ..models.tasks import Tasks


class TasksForm(ModelForm):
    class Meta:
        model = Tasks
        fields = ('version', 'key', 'summary', 'sprint', 'assignee',
                  'resource_type', 'story_link', 'estimation', 'estimation_done')
