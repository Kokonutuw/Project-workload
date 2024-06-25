from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Sum
from django.shortcuts import redirect
from django.utils.http import urlencode
from django.views.generic import DetailView
from ..forms.personnes import PersonneSearchForm
import calendar
import html

from django.shortcuts import render
from django.urls import reverse

from ..models.availability import Availability
from ..models.personnes import Personnes
from ..models.workload import Workload


class PersonneDetailView(DetailView):
    model = Personnes
    template_name = 'personnes/personne_detail.html'
    context_object_name = 'personne'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        personne = self.get_object()
        data_workload_person, data_workload_left_person, data_workload_done_person, label_personne = workload_per_month_for_person(
            personne.name)
        data_availability_person = availability_per_person(personne.name)
        context['data_workload_person'] = data_workload_person
        context['data_workload_left_person'] = data_workload_left_person
        context['data_workload_done_person'] = data_workload_done_person
        context['label_personne'] = label_personne
        context['data_availability_person'] = data_availability_person
        return context


def personne_detail(request, pk):
    selected = "personnes"
    print(selected)
    personne = Personnes.objects.get(pk=pk)
    total_availability = Availability.objects.filter(personne_availability__name=personne.name).aggregate(
        total=Sum('availability')).get('total') or 0

    data_workload_person, data_workload_left_person, data_workload_done_person, label_personne = workload_per_month_for_person(
        personne.name)

    data_availability_person = availability_per_person(personne.name)

    context = {
        'personne': personne,

        'data_workload_person': data_workload_person,
        'data_workload_left_person': data_workload_left_person,
        'data_workload_done_person': data_workload_done_person,
        'label_personne': label_personne,
        'data_availability_person': data_availability_person,
        'total_availability': total_availability
    }

    return render(request, 'personnes/personne_detail.html', locals())


@login_required
def personne_list(request):
    selected = "personnes"
    personnes_list = Personnes.objects.exclude(name="Nobody")
    for personne in personnes_list:
        if personne.name == "Nobody":
            pass

    if request.method == "POST":
        form = PersonneSearchForm(request.POST)
        if form.is_valid():
            base_url = reverse('personnes')
            query_string = urlencode(form.cleaned_data)
            url = '{}?{}'.format(base_url, query_string)
            return redirect(url)
    else:
        form = PersonneSearchForm()
        name_form = request.GET.get("name", "")
        resource_form = request.GET.get("resource_type", "")
        if name_form is not None:
            personnes_list = personnes_list.filter(name__icontains=name_form)
            form.initial['name'] = name_form
        if resource_form is not None:
            personnes_list = personnes_list.filter(resource_type__icontains=resource_form)
            form.initial['resource_type'] = resource_form

    paginator = Paginator(personnes_list.order_by('name'), 10)
    try:
        page = request.GET.get("page")
        if not page:
            page = 1
        personnes_list = paginator.page(page)
    except EmptyPage:
        personnes_list = paginator.page(paginator.num_pages())
    return render(request, "personnes/personne_list.html", locals())


def workload_per_month_for_person(person_name):
    person = Personnes.objects.filter(name=person_name)

    personne_workload_list = Workload.objects.filter(personne_workload=person[0])
    label_workload = []

    data_workload_person = []
    dico_workload_person = {}

    data_workload_done_person = []
    dico_workload_done_person = {}

    data_workload_left_person = []
    dico_workload_left_person = {}

    list_month = []

    available_months = Availability.objects.filter(personne_availability_id=1).values_list('month', flat=True)

    for month in available_months:
        month_name = calendar.month_abbr[month]
        month_name_formatted = month_name.capitalize()
        label_workload.append(month_name_formatted)
        list_month.append(month)
        for personne in personne_workload_list:
            if personne.month == month:
                dico_workload_person[month] = personne.workload
                dico_workload_done_person[month] = personne.done_workload
                dico_workload_left_person[month] = personne.workload - personne.done_workload
            elif month not in dico_workload_person.keys():
                dico_workload_person[month] = 0
                dico_workload_done_person[month] = 0
                dico_workload_left_person[month] = 0

    for i in list_month:
        data_workload_person.append(dico_workload_person.get(i, 0))
        data_workload_done_person.append(dico_workload_done_person.get(i, 0))
        data_workload_left_person.append(dico_workload_left_person.get(i, 0))

    return data_workload_person, data_workload_left_person, data_workload_done_person, label_workload


def availability_per_person(person_name):
    availabilities = Availability.objects.filter(personne_availability__name=person_name)
    data_availability = []

    for availability in availabilities:
        data_availability.append(availability.availability)

    return data_availability
