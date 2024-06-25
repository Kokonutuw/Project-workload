import datetime

from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F
from django.shortcuts import render
from django.urls import reverse

from ..models.availability import Availability
from ..models.personnes import Personnes
from ..models.workload import Workload
from ..models.sprints import Sprints


def count_workload_per_sprint_per_month(list_sprint, list_month):
    #on créé un dictionnaire pour stocker les nombres correspondants aux mois de l'année avec en clé le nombre de jour correspondant
    month_num = {"30": ["4", "6", "8", "9", "11"], "31": ["1", "3", "5", "7", "8", "10", "12"], "28": "2"}
    urls=[]
    data_sprint = {}

    #initialisation de variables correspondant aux couleurs, et à la variation de celles ci
    r = 10
    g = 100
    b = 100
    r_var = 10
    g_var = 10
    b_var = 20

    #on parcours la liste de sprints passée en paramètre de la fonction
    for sprint in list_sprint:
        urls.append(
            reverse("sprints") + "/" + str(sprint.id)+"/"
        )
        #initialisation de la variable count days qui stockera le nombre total de jours pour un sprint
        count_days = 0
        #on parcours une liste de mois passée en paramètre de la fonction, qui commence un mois avant la date actuelle et finit 6 mois après
        for month in list_month:
            #on vérifie si le début de notre sprint est dans le premier mois de la liste
            if sprint.start_date.month == month:
                #si oui, on vérifie si le mois de début du sprint est égal au mois de fin
                if sprint.start_date.month != sprint.end_date.month:
                    #si oui, on effectue les calculs récents ci dessous, en vérifiant le nombre de jours du mois de début
                    second_month_days = sprint.end_date.day
                    if str(sprint.start_date.month) in month_num["30"]:
                        first_month_days = 30 - sprint.start_date.day + 1
                        count_days = first_month_days + second_month_days
                    elif str(sprint.start_date.month) in month_num["31"]:
                        first_month_days = 31 - sprint.start_date.day + 1
                        count_days = first_month_days + second_month_days
                    elif str(sprint.start_date.month) in month_num["28"]:
                        first_month_days = 28 - sprint.start_date.day + 1
                        count_days = first_month_days + second_month_days
                    #on vérifie si le sprint est déjà dans notre dictionnaire
                    if not sprint.name in data_sprint.keys():
                        #si non, on l'y ajoute en lui donnant une couleur et des valeurs
                        data_sprint[sprint.name] = {"color": f"rgb({r + r_var},{g + g_var},{b + b_var},{0.6})",
                                                    "count": [sprint.estimation * first_month_days / count_days,
                                                              sprint.estimation * second_month_days / count_days]}

                    else:
                        #si oui, on lui ajoute simplement les valeurs
                        data_sprint[sprint.name]["count"].append(sprint.estimation * first_month_days / count_days)
                        data_sprint[sprint.name]["count"].append(sprint.estimation * second_month_days / count_days)



                else:
                    #si le sprint ne s'étend que sur un mois, on effectue les calculs ci dessous
                    if str(sprint.start_date.month) in month_num["30"]:
                        first_month_days = 30 - sprint.start_date.day + 1
                        count_days = first_month_days
                    elif str(sprint.start_date.month) in month_num["31"]:
                        first_month_days = 31 - sprint.start_date.day + 1
                        count_days = first_month_days
                    elif str(sprint.start_date.month) in month_num["28"]:
                        first_month_days = 28 - sprint.start_date.day + 1
                        count_days = first_month_days
                    #et on effectue les mêmes vérifications que dans l'autre cas
                    if not sprint.name in data_sprint.keys():
                        data_sprint[sprint.name] = {"color": f"rgb({r},{g},{b},{0.6})",
                                                    "count": [sprint.estimation]}
                    else:
                        data_sprint[sprint.name]["count"].append(sprint.estimation)
                break
            elif sprint.end_date.month!=month:
                #si le mois de début et le mois de fin du sprint ne correspondent pas au mois actuel, on ajoute un 0 à ses valeurs, ou on créé le sprint avec un 0 dans ses valeurs
                if sprint.name in data_sprint.keys():
                    data_sprint[sprint.name]["count"].append(0)
                else:
                    data_sprint[sprint.name] = {"color": f"rgb({r},{g},{b},{0.6})",
                                                "count": [0]}
        #après chaque sprint, on modifie les valeurs de variation des couleurs en faisant attention qu'aucune d'elle ne prenne une valeur illogique
        if r-r_var>255:
            r=0+r_var
        if g+g_var>255:
            g=0+g_var
        if b+b_var>255:
            b=0-b_var
        r+=r_var
        g+=g_var
        b+=b_var
    return data_sprint,urls



def dashboard_view(request):
    selected = "dashboard"
    person_id = 1

    label_sprint = []
    list_month = []
    list_availabilities_fs = Availability.objects.filter(
        personne_availability__in=Personnes.objects.filter(resource_type='FULLSTACK').exclude(name="Nobody"))
    list_workload_fs = Workload.objects.filter(
        personne_workload__in=Personnes.objects.filter(resource_type='FULLSTACK'))
    label_availability = []
    data_availability_fs = []
    data_workload_fs = []
    data_workload_done_fs = []
    data_workload_left_fs = []

    # display Previous month and the next 6 month
    # labels = month
    for a in Availability.objects.filter(personne_availability_id=1):
        datetime_object = datetime.datetime.strptime(str(a.month), "%m")
        month_name = datetime_object.strftime("%b")
        label_availability.append(month_name)
        label_sprint.append(month_name)

        #initialisation de la variable list_month qui sert à lister les mois qu'on prend en compte
        list_month.append(a.month)
        # Count Fullstack availability
        count_total = list_availabilities_fs.filter(year=a.year).filter(month=a.month).aggregate(
            total=Sum(F('availability'))).get('total')
        count_total = count_total if count_total else 0
        data_availability_fs.append(count_total)

        # Count Fullstack workload
        count_total = list_workload_fs.filter(year=a.year).filter(month=a.month).aggregate(
            total=Sum(F('workload'))).get('total')
        count_total = count_total if count_total else 0
        data_workload_fs.append(count_total)
        tmp_left = count_total

        count_total = list_workload_fs.filter(year=a.year).filter(month=a.month).aggregate(
            total=Sum(F('done_workload'))).get('total')
        count_total = count_total if count_total else 0
        data_workload_done_fs.append(count_total)
        data_workload_left_fs.append(tmp_left - count_total)


    list_sprint = Sprints.objects.exclude(start_date=None)
    count_workload_sprints=count_workload_per_sprint_per_month(list_sprint, list_month)
    data_sprint = count_workload_sprints[0]
    urls = count_workload_sprints[1]
    urls_string=""
    for url in urls:
        urls_string+=f"{url},"
    urls_string=urls_string[0:len(urls_string)-1]

    return render(request, 'dashboard/dashboard.html', locals())
# la valeur de maxence passe le 5 eme mois a la place du 6 eme
