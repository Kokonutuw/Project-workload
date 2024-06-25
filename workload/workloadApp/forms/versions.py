from django.forms import ModelForm

from ..models.versions import Versions


class VersionsForm(ModelForm):
    class Meta:
        model = Versions
        fields = ('name', 'first_sprint', 'last_sprint', 'start_date_dev', 'end_date_dev',
                  'start_date_qa', 'end_date_qa', 'stories', 'bugs', 'estimation', 'estimation_remaining')
