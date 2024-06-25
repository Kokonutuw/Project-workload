from django.forms import CharField, Form


class PersonneSearchForm(Form):
    name = CharField(max_length=100, required=False)
    resource_type = CharField(max_length=100, required=False)
