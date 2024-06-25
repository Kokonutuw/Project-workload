import json
from datetime import datetime

from django.db.models import Sum, F
from django.shortcuts import render


from ..models.availability import Availability
from ..models.epic import Epic
from ..models.personnes import Personnes
from ..models.stories_epic import Stories_epic


def roadmap_view(request):
    epics = Epic.objects.all()
    epic_labels = []
    epic_data = []
    current_date = datetime.now().date()
    epics_color={}
    for epic in epics:


        epic_estimation = 0
        stories = Stories_epic.objects.filter(parent_key=epic.issue_key)
        for story in stories:
            epic_estimation += story.estimate_fs
        epic.estimation = epic_estimation

        start_date = epic.start_date
        end_date = epic.end_date
        if end_date is None or current_date >= end_date:
            continue

        epic_labels.append(epic.issue_key)
        duration = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month) + 1

        month_diff = (start_date.month - current_date.month +1 ) % 12

        epic_workload = [0] * 12

        total_workload = int(epic.estimation)

        if duration > 0:
            workload_per_month = total_workload // duration
            remaining_workload = total_workload % duration

            for i in range(duration):
                month_index = (month_diff + i) % 12

                if remaining_workload > 0:
                    epic_workload[month_index] = workload_per_month + 1
                    remaining_workload -= 1
                else:
                    epic_workload[month_index] = workload_per_month

        print(epic_labels)
        print(epics_color)
        epics_color[epic.issue_key] = epic.color
        epic_data.append(epic_workload)

    # Récupérer les données d'availability pour FullStack
    list_availabilities_fs = Availability.objects.filter(
        personne_availability__in=Personnes.objects.filter(resource_type='FULLSTACK').exclude(name="Nobody"))
    label_availability = []
    data_availability_fs = []

    for a in Availability.objects.filter(personne_availability_id=1):
        month_name = datetime.strptime(str(a.month), "%m").strftime("%b")
        label_availability.append(month_name)

        count_total = list_availabilities_fs.filter(year=a.year, month=a.month).aggregate(
            total=Sum(F('availability'))).get('total')
        count_total = count_total if count_total else 0
        data_availability_fs.append(count_total)

    context = {
        'epic_labels': json.dumps(epic_labels),
        'epic_data': json.dumps(epic_data),
        'data_availability_fs': json.dumps(data_availability_fs),
        'epics_color': json.dumps(epics_color)
    }

    return render(request, 'roadmap/roadmap.html', context)
