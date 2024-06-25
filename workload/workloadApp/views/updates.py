import csv
import calendar
import datetime
from random import randint

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from django.utils.dateparse import parse_datetime

from management.Utils import utils_api_jira, utils
from ..models.availability import Availability
from ..models.epic import Epic
from ..models.personnes import Personnes
from ..models.projects import Projects
from ..models.products import Products
from ..models.sprints import Sprints
from ..models.stories_customer import Stories_customer
from ..models.stories_epic import Stories_epic
from ..models.tasks import Tasks
from ..models.updates import Updates
from ..models.stories import Stories
from ..models.projects_customers import ProjectsCustomers
from ..models.holidays import Holidays
from ..models.workload import Workload


def update_view(request):
    selected = "updates"
    allowed_user_id = 1
    if request.user.id != allowed_user_id:
        return HttpResponseForbidden("Forbidden Access.")
    updates = Updates.objects.get(id=1)
    return render(request, 'updates/updates.html', {'selected': selected, 'updates': updates})


# @login_required
def import_task_from_jira(request):
    print('import all task for Cloud Si')
    return update_view(request)


def import_projects_task_from_jira(request, pk):
    print('import task for', pk)
    project = Projects.objects.get(id=pk)
    list_issues = utils_api_jira.get_all_issue_from_project(project.key)
    nb_task = 0
    nb_story = 0
    nb_bugs = 0
    print(list_issues)
    for issue in list_issues:
        task_type = issue['fields']['issuetype']['name']
        task_status = issue['fields']['status']['name']
        task_key = issue['key']
        task_summary = issue['fields']['summary']
        original_estimation = utils_api_jira.get_task_estimation(issue)
        done_estimation = utils.get_task_estimation_done(task_status, original_estimation)
        task_ressource_type = utils_api_jira.get_task_ressource_type(issue)
        if task_ressource_type is None:
            task_ressource_type = ''
        task_assignee = str(utils_api_jira.get_task_assignee(issue))
        if task_assignee == '':
            task_assignee = 'Nobody'

        # get Story details
        linked_story = {
            'sprint': '',
            'start_date': '',
            'end_date': '',
            'version': ''
        }
        linked_story_key = utils_api_jira.get_story_linked(issue)
        if linked_story_key != '':
            linked_story = utils_api_jira.get_story_details(linked_story_key)

        task_sprint = linked_story['sprint']
        print("linked_story", linked_story)
        if task_sprint == '':
            task_sprint = 'No Sprint'
        if task_type == 'Task':
            nb_task = nb_task + 1
        elif task_type == 'Bug':
            nb_bugs = nb_bugs + 1
        elif task_type == 'Story':
            nb_story = nb_story + 1

        if task_sprint != 'No Sprint':
            try:
                register_sprint = Sprints.objects.get(name=task_sprint)
            except ObjectDoesNotExist:
                register_sprint = Sprints(name=task_sprint,
                                          start_date=parse_datetime(str(linked_story['start_date'])),
                                          end_date=parse_datetime(str(linked_story['end_date'])),
                                          estimation=original_estimation,
                                          estimation_remaining=original_estimation - done_estimation,
                                          resources_types=task_assignee)
            else:
                register_sprint.estimation = register_sprint.estimation + original_estimation
                register_sprint.estimation_remaining = register_sprint.estimation_remaining + original_estimation - done_estimation
                if task_assignee not in register_sprint.resources_types:
                    register_sprint.resources_types = register_sprint.resources_types + " - " + task_assignee

            register_sprint.save()

        try:
            task = Tasks.objects.get(key=task_key)
            task.summary = task_summary
            task.version = linked_story['version']
            task.sprint = task_sprint
            task.assignee = task_assignee
            task.resource_type = task_ressource_type
            task.story_link = linked_story_key
            task.estimation = original_estimation
            task.estimation_done = done_estimation
            task.status = task_status
            if linked_story['start_date'] is not None and str(linked_story['start_date']) != '':
                task.start_date = parse_datetime(str(linked_story['start_date']))
            if linked_story['end_date'] is not None and str(linked_story['end_date']) != '':
                task.end_date = parse_datetime(str(linked_story['end_date']))

            if task_type == 'Task' or task_type == 'Bug':
                task.save()
        except ObjectDoesNotExist:

            task = Tasks(
                key=task_key,
                summary=task_summary,
                version=linked_story['version'],
                sprint=task_sprint,
                assignee=task_assignee,
                resource_type=task_ressource_type,
                story_link=linked_story_key,
                estimation=original_estimation,
                estimation_done=done_estimation,
                status=task_status
            )
            start_date = ''
            end_date = ''
            if linked_story['start_date'] is not None and str(linked_story['start_date']) != '':
                task.start_date = parse_datetime(str(linked_story['start_date']))
            if linked_story['end_date'] is not None and str(linked_story['end_date']) != '':
                task.end_date = parse_datetime(str(linked_story['end_date']))
            if task_type == 'Task' or task_type == 'Bug':
                task.save()

    project.tasks = nb_task
    project.bugs = nb_bugs
    project.stories = nb_story
    project.save()
    return redirect('projects')


def updates_import_product_stories(request, pk):
    print('import stories for', pk)
    product = Products.objects.get(id=pk)
    list_issues = utils_api_jira.get_all_issue_from_project(product.key)
    nb_task = 0
    nb_story = 0
    nb_bugs = 0
    for issue in list_issues:
        story_key = issue['key']
        story_summary = issue['fields']['summary']
        story_type = issue['fields']['issuetype']['name']
        details = utils_api_jira.get_story_details(story_key)
        story_version = details['version']
        story_sprint = details['sprint']
        story_status = issue['fields']['status']['name']
        assignee = utils_api_jira.get_task_assignation(issue)
        story_estimation = 0
        story_estimation_done = 0
        tasks = []
        for link_issue in issue['fields']['issuelinks']:
            try:
                task = utils_api_jira.get_task(link_issue['inwardIssue']['key'])
                tmp_estimation = utils_api_jira.get_task_estimation(task)
                story_estimation = story_estimation + tmp_estimation
                story_estimation_done = story_estimation_done + utils.get_task_estimation_done(
                    task['fields']['status']['name'], tmp_estimation)
                tasks.append(str(link_issue['inwardIssue']['key']))
            except KeyError:
                print('Error key', issue['key'])
                pass
            except TypeError:
                print('Error type', issue['key'])
                pass

        try:
            story = Stories.objects.get(key=story_key)
            story.summary = story_summary
            story.version = story_version
            story.sprint = story_sprint
            story.assignee = assignee
            story.tasks_link = tasks
            story.estimation = story_estimation
            story.estimation_done = story_estimation_done
            story.type = story_type
            story.status = story_status
            story.save()
        except ObjectDoesNotExist:
            story = Stories(
                key=story_key,
                summary=story_summary,
                version=story_version,
                sprint=story_sprint,
                assignee=assignee,
                tasks_link=tasks,
                estimation=story_estimation,
                estimation_done=story_estimation_done,
                status=story_status,
                type=story_type
            )
            story.save()

        if story_type == 'Task':
            nb_task = nb_task + 1
        elif story_type == 'Bug':
            nb_bugs = nb_bugs + 1
        elif story_type == 'Story':
            nb_story = nb_story + 1

    product.tasks = nb_task
    product.bugs = nb_bugs
    product.stories = nb_story
    product.save()
    return redirect('products')


def updates_import_projects_customers_stories(request, pk):
    print('import stories for', pk)
    project = ProjectsCustomers.objects.get(id=pk)
    list_issues = utils_api_jira.get_all_issue_from_project(project.key)
    nb_task = 0
    nb_story = 0
    nb_bugs = 0
    for issue in list_issues:
        task_type = issue['fields']['issuetype']['name']

        if task_type == 'Task':
            nb_task = nb_task + 1
        elif task_type == 'Bug':
            nb_bugs = nb_bugs + 1
        elif task_type == 'Story':
            nb_story = nb_story + 1

    project.tasks = nb_task
    project.bugs = nb_bugs
    project.stories = nb_story
    project.save()
    return redirect('projects_customers')


def import_all_projects_task_from_jira(request):
    print('All project update')
    list_projects = Projects.objects.all()
    print('Delete All sprints')
    Sprints.objects.all().delete()
    for project in list_projects:
        print('All project update', project.key)
        import_projects_task_from_jira(request, project.id)

    u = Updates.objects.get(id=1)
    u.last_cmd = 'Update All Tech Projects OK'
    u.save()
    return redirect('updates')


def import_project_from_jira(request):
    print('import all project for Cloud Si')
    # Delete all task
    projects = utils_api_jira.get_all_project_by_category('TECH CLOUD SOFTWARE')
    for prj in projects:
        try:
            p = Projects.objects.get(key=prj['key'])
            p.key = prj['key']
            p.name = prj['name']
            p.category = prj['projectCategory']['name']
            p.save()
        except ObjectDoesNotExist:
            p = Projects(key=prj['key'], name=prj['name'], category=prj['projectCategory']['name'])
            p.save()
            pass
    return redirect('projects')


def import_product_from_jira(request):
    print('import all Velco Products')
    products = utils_api_jira.get_all_project_by_category('VELCO PRODUCTS')
    for prj in products:
        try:
            p = Products.objects.get(key=prj['key'])
            p.key = prj['key']
            p.name = prj['name']
            p.category = prj['projectCategory']['name']
            p.save()
        except ObjectDoesNotExist:
            p = Products(key=prj['key'], name=prj['name'], category=prj['projectCategory']['name'])
            p.save()
            pass
    return redirect('products')


def import_all_products_stories_from_jira(request):
    print('All product update')
    list_products = Products.objects.all()
    for product in list_products:
        print('All product update', product.key)
        updates_import_product_stories(request, product.id)
    return redirect('products')


def updates_import_project_customer_stories(pk):
    print('import stories for', pk)
    project = ProjectsCustomers.objects.get(id=pk)
    list_issues = utils_api_jira.get_all_issue_not_end_from_customer_project(project.key)
    nb_task = 0
    nb_story = 0
    nb_bugs = 0
    for issue in list_issues:
        story_key = issue['key']
        story_summary = issue['fields']['summary']
        story_type = issue['fields']['issuetype']['name']
        details = utils_api_jira.get_story_details(story_key)
        story_version = details['version']
        story_sprint = details['sprint']
        story_status = issue['fields']['status']['name']
        assignee = utils_api_jira.get_task_assignation(issue)
        story_estimation = 0
        story_estimation_done = 0
        tasks = []
        if str(story_status) != 'Done' and str(story_status) != 'WONT DO':
            for link_issue in issue['fields']['issuelinks']:
                try:
                    task = utils_api_jira.get_task(link_issue['inwardIssue']['key'])
                    tmp_estimation = utils_api_jira.get_task_estimation(task)
                    story_estimation = story_estimation + tmp_estimation
                    story_estimation_done = story_estimation_done + utils.get_task_estimation_done(
                        task['fields']['status']['name'], tmp_estimation)
                    tasks.append(str(link_issue['inwardIssue']['key']))
                except KeyError:
                    print('Error key', issue['key'])
                    pass
                except TypeError:
                    print('Error type', issue['key'])
                    pass

            try:
                story = Stories_customer.objects.get(key=story_key)
                story.summary = story_summary
                story.version = story_version
                story.sprint = story_sprint
                story.assignee = assignee
                story.tasks_link = tasks
                story.estimation = story_estimation
                story.estimation_done = story_estimation_done
                story.type = story_type
                story.status = story_status
                story.save()
            except ObjectDoesNotExist:
                story = Stories_customer(
                    key=story_key,
                    summary=story_summary,
                    version=story_version,
                    sprint=story_sprint,
                    assignee=assignee,
                    tasks_link=tasks,
                    estimation=story_estimation,
                    estimation_done=story_estimation_done,
                    status=story_status,
                    type=story_type
                )
                story.save()

            if story_type == 'Task':
                nb_task = nb_task + 1
            elif story_type == 'Bug':
                nb_bugs = nb_bugs + 1
            elif story_type == 'Story':
                nb_story = nb_story + 1

    project.tasks = nb_task
    project.bugs = nb_bugs
    project.stories = nb_story
    project.save()


def import_all_project_customer_stories_from_jira(request):
    print('All projects customer update')
    Stories_customer.objects.all().delete()
    list_projects = ProjectsCustomers.objects.all()
    for project in list_projects:
        print('All projects customer update', project.key)
        updates_import_project_customer_stories(project.id)
    return redirect('projects_customers')


def import_all_epic_from_jira(request):
    epic_list = utils_api_jira.get_epic()
    colors = {}
    used_numbers=[]
    for epic_data in epic_list:
        import_epic_from_jira(request, epic_data, colors,used_numbers)

    return redirect('epic')


def import_epic_from_jira(request, epic_data, colors,used_numbers):
    epic_key = epic_data['key']
    epic_summary = epic_data['fields']['summary']
    epic_estimation = epic_data['fields'].get('estimation', 0)
    epic_estimation_remaining = epic_data['fields'].get('estimation_remaining', 0)
    epic_key_id = epic_data['id']
    epic_key_start = ""
    color_list=["#B4B2FF","#b2d7ff","#b2ffb4","#dbb2ff","#ffb4b2","#928288","#013385","#BD326A","#82C9E0","#82e0c8"]
    for i in epic_key:
        if not i == "-":
            epic_key_start += i
        else:
            break
    if epic_key_start not in colors.keys():
        randnum=randint(0,9)
        while randnum in used_numbers:
            randnum=randint(0,9)
        used_numbers.append(randnum)
        epic_color=color_list[randnum]
        colors[epic_key_start]=epic_color

    else:
        epic_color=colors[epic_key_start]


    try:
        epic = Epic.objects.get(issue_key=epic_key)
        epic.summary = epic_summary
        epic.estimation = epic_estimation
        epic.estimation_remaining = epic_estimation_remaining

        epic.color=epic_color

        epic.save()
    except Epic.DoesNotExist:
        epic = Epic.objects.create(
            issue_key=epic_key,
            summary=epic_summary,
            estimation=epic_estimation,
            estimation_remaining=epic_estimation_remaining,
            key_id=epic_key_id,
            color=epic_color
        )

    return epic


def import_all_epic_storie_from_jira(request):
    epic_list = Epic.objects.all()
    for epic in epic_list:
        epic_storie_list = utils_api_jira.get_epic_stories(epic.issue_key)
        for epic_storie in epic_storie_list:
            import_epic_storie_from_jira(request, epic_storie)

    return redirect('epic_storie')


def import_epic_storie_from_jira(request, epic_data):
    storie_key = epic_data['key']
    storie_summary = epic_data['fields']['summary']
    storie_status = epic_data['fields']['status']['name']
    storie_type = epic_data['fields']['issuetype']['name']
    storie_epic = epic_data['fields']['parent']['fields']['summary']
    storie_estimate_fs = epic_data['fields']['customfield_10075']
    if storie_estimate_fs == None:
        storie_estimate_fs = 0
    storie_parent_key = epic_data['fields']['parent']['key']

    try:
        epic_storie = Stories_epic.objects.get(key=storie_key)
        epic_storie.summary = storie_summary
        epic_storie.status = storie_status
        epic_storie.type = storie_type
        epic_storie.epic = storie_epic
        epic_storie.estimate_fs = storie_estimate_fs
        epic_storie.parent_key = storie_parent_key
        epic_storie.save()
    except Stories_epic.DoesNotExist:
        epic_storie = Stories_epic.objects.create(
            key=storie_key,
            summary=storie_summary,
            status=storie_status,
            type=storie_type,
            epic=storie_epic,
            estimate_fs=storie_estimate_fs,
            parent_key=storie_parent_key,
        )
    return epic_storie


def clear_outdated_data(request):
    print('Synchro projects tech')
    list_projects = Projects.objects.all()
    for project in list_projects:
        exist = utils_api_jira.check_if_project_exist(project.key)
        if not exist:
            print("Delete ", project.key)
            project.delete()
    print('Synchro tasks')
    list_tasks = Tasks.objects.all()
    for task in list_tasks:
        exist = utils_api_jira.check_if_task_exist(task.key)
        if not exist:
            print("Delete ", task.key)
            task.delete()
    print('Synchro stories')
    list_stories = Stories.objects.all()
    for story in list_stories:
        exist = utils_api_jira.check_if_task_exist(story.key)
        if not exist:
            print("Delete ", story.key)
            story.delete()
    u = Updates.objects.get(id=1)
    u.last_cmd = 'Synchro Jira OK'
    u.save()
    return redirect('updates')


def clear_all_task(request):
    print('Clear all task')
    Tasks.objects.all().delete()
    u = Updates.objects.get(id=1)
    u.last_cmd = 'All task cleared'
    u.save()
    return redirect('updates')


def delete_and_update_holidays(request):
    print('Delete holidays')
    Holidays.objects.all().delete()
    print('Import Holidays')
    # open csv file
    reader = csv.DictReader(open('export_files/Timmi Absences.csv', encoding='utf-8'), delimiter=';')
    for row in reader:
        holiday_start_date = parse_datetime(
            row['START_DATE'][6:10] + '-' + row['START_DATE'][3:5] + '-' + row['START_DATE'][0:2])
        holiday_end_date = parse_datetime(
            row['END_DATE'][6:10] + '-' + row['END_DATE'][3:5] + '-' + row['END_DATE'][0:2])
        print('{} {} {}'.format('test', holiday_start_date, holiday_end_date))
        duration = row['DURATION']
        list_p = Personnes.objects.filter(last_name=row['LAST_NAME']).exclude(name="Nobody")
        personne = list_p[0]
        holiday = Holidays(
            start_date=holiday_start_date,
            end_date=holiday_end_date,
            duration=float(str(duration).replace(',', '.')),
            person_holidays=personne
        )
        holiday.save()
        print('{} {} {} {} {}'.format(
            row['LAST_NAME'],
            row['FIRST_NAME'],
            row['START_DATE'],
            row['END_DATE'],
            row['DURATION'],
        ))
    u = Updates.objects.get(id=1)
    u.last_cmd = 'Synchro Holidays OK'
    u.save()
    return redirect('updates')


def update_availability_list(list, datas):
    found = 0
    for available in list:
        if available['person'] == datas['person'] and available['month'] == \
                datas['month'] and available['year'] == datas['year']:
            available['duration'] = available['duration'] - datas['duration']
            found = 1
    # if not found, we need to do a new init
    if found == 0:
        list.append({'person': datas['person'],
                     'duration': 0,
                     'month': datas['month'],
                     'year': datas['year']})
    return list


# update availability for last month and 6 next month
def init_availability():
    list = []
    list_person = Personnes.objects.exclude(name="Nobody")
    for person in list_person:
        first_date = (datetime.date.today() - datetime.timedelta(days=31))
        date = parse_datetime(str(first_date)[0:8] + '01')
        days_on_month = calendar.monthrange(date.year, date.month)[1]
        datas = {
            'person': person,
            'duration': utils.count_week_days(date, days_on_month),
            'month': date.month,
            'year': date.year
        }
        list.append(datas)
        inc = 0
        while inc <= 7:
            date = date + datetime.timedelta(days=calendar.monthrange(date.year, date.month)[1])
            days_on_month = calendar.monthrange(date.year, date.month)[1]
            datas = {
                'person': person,
                'duration': utils.count_week_days(date, days_on_month),
                'month': date.month,
                'year': date.year
            }
            list.append(datas)
            inc = inc + 1
    return list


def calculate_unavailability_per_person_per_month(request):
    list_person = Personnes.objects.exclude(name="Nobody")
    availability = init_availability()
    for person in list_person:
        list_holiday = Holidays.objects.filter(person_holidays=person)
        for holiday in list_holiday:
            if holiday.start_date.month == holiday.end_date.month:
                availability = update_availability_list(availability, {'person': holiday.person_holidays,
                                                                       'duration': holiday.duration,
                                                                       'month': holiday.start_date.month,
                                                                       'year': holiday.start_date.year})
            else:
                end_first_month = parse_datetime(str(holiday.start_date)[0:8] +
                                                 str(calendar.monthrange(holiday.start_date.year,
                                                                         holiday.start_date.month)[1]))
                start_second_month = parse_datetime(str(holiday.end_date)[0:8] + '01')
                print("TEST DKE", holiday.start_date, holiday.end_date)
                day_first_month = (end_first_month.date() - holiday.start_date).days
                day_second_month = (holiday.end_date - start_second_month.date()).days

                week_day_first_month = utils.count_week_days(holiday.start_date, day_first_month)
                week_day_last_month = utils.count_week_days(start_second_month, day_second_month)
                availability = update_availability_list(availability, {'person': holiday.person_holidays,
                                                                       'duration': week_day_first_month,
                                                                       'month': holiday.start_date.month,
                                                                       'year': holiday.start_date.year})
                availability = update_availability_list(availability, {'person': holiday.person_holidays,
                                                                       'duration': week_day_last_month,
                                                                       'month': holiday.end_date.month,
                                                                       'year': holiday.end_date.year})

    Availability.objects.all().delete()
    for a in availability:
        ratio = 0.7
        if a['person'].email == 'pierre.s@velco.fr':
            ratio = 0.5
        if a['person'].email == 'wulfran@velco.fr':
            ratio = 0.3
        av = Availability(month=a['month'], year=a['year'], availability=(a['duration'] * ratio),
                          total_availability=a['duration'], personne_availability=a['person'])
        av.save()

    u = Updates.objects.get(id=1)
    u.last_cmd = 'Update Availability OK'
    u.save()
    return redirect('updates')


def update_workload_list(list_entry, datas):
    found = 0
    for work in list_entry:
        if work['person'].name != "Nobody":
            if work['person'] == datas['person'] and work['month'] == \
                    datas['month'] and work['year'] == datas['year']:
                work['estimation'] = work['estimation'] + datas['estimation']
                work['estimation_done'] = work['estimation_done'] + datas['estimation_done']
                found = 1
    # if not found, we need to do a new init
    if found == 0:
        list_entry.append({'person': datas['person'],
                           'estimation': datas['estimation'],
                           'estimation_done': datas['estimation_done'],
                           'month': datas['month'],
                           'year': datas['year']})
    return list_entry


def calculate_workload_by_person(id):
    workload = []
    person = Personnes.objects.get(id=id).exclude(name="Nobody")
    Workload.objects.filter(personne_workload=person).delete()
    list_task = Tasks.objects.filter(assignee=person.name)
    for task in list_task:
        if task.start_date is not None and task.end_date is not None:
            if task.start_date.month == task.end_date.month:
                workload = update_workload_list(workload, {'person': person,
                                                           'estimation': task.estimation,
                                                           'estimation_done': task.estimation_done,
                                                           'month': task.start_date.month,
                                                           'year': task.start_date.year})
            else:
                end_first_month = parse_datetime(str(task.start_date)[0:8] +
                                                 str(calendar.monthrange(task.start_date.year,
                                                                         task.start_date.month)[1]))
                start_second_month = parse_datetime(str(task.end_date)[0:8] + '01')
                day_first_month = (end_first_month - parse_datetime(str(task.start_date))).days
                day_second_month = (parse_datetime(str(task.end_date)) - start_second_month).days

                week_day_first_month = utils.count_week_days(task.start_date, day_first_month)
                week_day_last_month = utils.count_week_days(start_second_month, day_second_month)
                if week_day_last_month > 1:
                    week_day_last_month = week_day_last_month - 1

                total_day = week_day_first_month + week_day_last_month
                estimation_first_month = week_day_first_month * (task.estimation / total_day)
                estimation_second_month = week_day_last_month * (task.estimation / total_day)

                done_first_month = week_day_first_month * (task.estimation_done / total_day)
                done_second_month = week_day_last_month * (task.estimation_done / total_day)

                workload = update_workload_list(workload, {'person': person,
                                                           'estimation': estimation_first_month,
                                                           'estimation_done': done_first_month,
                                                           'month': task.start_date.month,
                                                           'year': task.start_date.year})
                workload = update_workload_list(workload, {'person': person,
                                                           'estimation': estimation_second_month,
                                                           'estimation_done': done_second_month,
                                                           'month': task.end_date.month,
                                                           'year': task.end_date.year})
        else:
            inc = 1
            # print('charge non planifié')

    for w in workload:
        if w['person'].email != 'marion@velco.fr' and w['person'].email != 'sebastien@velco.fr' and w[
            'person'].email != 'franck@velco.fr':
            work = Workload(month=w['month'], year=w['year'], workload=w['estimation'],
                            done_workload=w['estimation_done'], personne_workload=w['person'])
            work.save()


def calculate_workload_per_person_per_month(request):
    Workload.objects.all().delete()
    list_person = Personnes.objects.exclude(name="Nobody")
    workload = []
    for person in list_person:
        if person.name != "Nobody":
            list_task = Tasks.objects.filter(assignee=person.name)
            for task in list_task:
                if task.start_date is not None and task.end_date is not None:
                    if task.start_date.month == task.end_date.month:
                        workload = update_workload_list(workload, {'person': person,
                                                                   'estimation': task.estimation,
                                                                   'estimation_done': task.estimation_done,
                                                                   'month': task.start_date.month,
                                                                   'year': task.start_date.year})
                    else:
                        end_first_month = parse_datetime(str(task.start_date)[0:8] +
                                                         str(calendar.monthrange(task.start_date.year,
                                                                                 task.start_date.month)[1]))
                        start_second_month = parse_datetime(str(task.end_date)[0:8] + '01')
                        day_first_month = (end_first_month - parse_datetime(str(task.start_date))).days
                        day_second_month = (parse_datetime(str(task.end_date)) - start_second_month).days

                        week_day_first_month = utils.count_week_days(task.start_date, day_first_month)
                        week_day_last_month = utils.count_week_days(start_second_month, day_second_month)
                        if week_day_last_month > 1:
                            week_day_last_month = week_day_last_month - 1

                        total_day = week_day_first_month + week_day_last_month
                        estimation_first_month = week_day_first_month * (task.estimation / total_day)
                        estimation_second_month = week_day_last_month * (task.estimation / total_day)

                        done_first_month = week_day_first_month * (task.estimation_done / total_day)
                        done_second_month = week_day_last_month * (task.estimation_done / total_day)

                        workload = update_workload_list(workload, {'person': person,
                                                                   'estimation': estimation_first_month,
                                                                   'estimation_done': done_first_month,
                                                                   'month': task.start_date.month,
                                                                   'year': task.start_date.year})
                        workload = update_workload_list(workload, {'person': person,
                                                                   'estimation': estimation_second_month,
                                                                   'estimation_done': done_second_month,
                                                                   'month': task.end_date.month,
                                                                   'year': task.end_date.year})
                else:
                    inc = 1
                    # print('charge non planifié')

    list_task_unassignee = Tasks.objects.filter(assignee='Nobody')
    for task in list_task_unassignee:
        if task.start_date is not None and task.end_date is not None:
            if task.start_date.month == task.end_date.month:
                workload = update_workload_list(workload, {'person': person,
                                                           'estimation': task.estimation,
                                                           'estimation_done': task.estimation_done,
                                                           'month': task.start_date.month,
                                                           'year': task.start_date.year})
            else:
                end_first_month = parse_datetime(str(task.start_date)[0:8] +
                                                 str(calendar.monthrange(task.start_date.year,
                                                                         task.start_date.month)[1]))
                start_second_month = parse_datetime(str(task.end_date)[0:8] + '01')
                day_first_month = (end_first_month - parse_datetime(str(task.start_date))).days
                print('TEST', str(task.end_date), start_second_month)
                print('TEST-1', task.key)
                day_second_month = (parse_datetime(str(task.end_date)) - start_second_month).days

                week_day_first_month = utils.count_week_days(task.start_date, day_first_month)
                week_day_last_month = utils.count_week_days(start_second_month, day_second_month)

                estimation_first_month = task.estimation * (task.estimation / week_day_first_month)
                estimation_second_month = task.estimation * (task.estimation / week_day_last_month)

                done_first_month = task.estimation_done * (task.estimation_done / week_day_first_month)
                done_second_month = task.estimation_done * (task.estimation_done / week_day_last_month)

                workload = update_workload_list(workload, {'person': person,
                                                           'estimation': estimation_first_month,
                                                           'estimation_done': done_first_month,
                                                           'month': task.start_date.month,
                                                           'year': task.start_date.year})
                workload = update_workload_list(workload, {'person': person,
                                                           'estimation': estimation_second_month,
                                                           'estimation_done': done_second_month,
                                                           'month': task.end_date.month,
                                                           'year': task.end_date.year})
        else:
            inc = 1
            # print('charge non planifié')

    for w in workload:
        if w['person'].email != 'marion@velco.fr' and w['person'].email != 'sebastien@velco.fr' and w[
            'person'].email != 'franck@velco.fr':
            work = Workload(month=w['month'], year=w['year'], workload=w['estimation'],
                            done_workload=w['estimation_done'], personne_workload=w['person'])
            work.save()

    u = Updates.objects.get(id=1)
    u.last_cmd = 'Update Workload OK'
    u.save()
    return redirect('updates')


# TO TEST
def updates_admin_task(request):
    Stories.objects.filter(key__startswith="SA-").delete()
    list_stories = utils_api_jira.get_all_issue_from_project('SA')

    for issue in list_stories:
        story_key = issue['key']
        story_summary = issue['fields']['summary']
        story_type = issue['fields']['issuetype']['name']
        details = utils_api_jira.get_story_details(story_key)
        story_version = details['version']
        story_sprint = details['sprint']
        story_status = issue['fields']['status']['name']
        assignee = utils_api_jira.get_task_assignation(issue)
        story_estimation = 0
        story_estimation_done = 0
        tasks = []
        for link_issue in issue['fields']['issuelinks']:
            try:
                task = utils_api_jira.get_task(link_issue['inwardIssue']['key'])
                tmp_estimation = utils_api_jira.get_task_estimation(task)
                story_estimation = story_estimation + tmp_estimation
                story_estimation_done = story_estimation_done + utils.get_task_estimation_done(
                    task['fields']['status']['name'], tmp_estimation)
                tasks.append(str(link_issue['inwardIssue']['key']))
            except KeyError:
                print('Error key', issue['key'])
                pass
            except TypeError:
                print('Error type', issue['key'])
                pass

        try:
            story = Stories.objects.get(key=story_key)
            story.summary = story_summary
            story.version = story_version
            story.sprint = story_sprint
            story.assignee = assignee
            story.tasks_link = tasks
            story.estimation = story_estimation
            story.estimation_done = story_estimation_done
            story.type = story_type
            story.status = story_status
            story.save()
        except ObjectDoesNotExist:
            story = Stories(
                key=story_key,
                summary=story_summary,
                version=story_version,
                sprint=story_sprint,
                assignee=assignee,
                tasks_link=tasks,
                estimation=story_estimation,
                estimation_done=story_estimation_done,
                status=story_status,
                type=story_type
            )
            story.save()
    u = Updates.objects.get(id=1)
    u.last_cmd = 'Update Admin task OK'
    u.save()
    return redirect('updates')
