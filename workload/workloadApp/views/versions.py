from django.core.paginator import Paginator, EmptyPage
from django.shortcuts import render, redirect
from django.utils.dateparse import parse_datetime

from ..models.versions import Versions
from ..models.tasks import Tasks
from management.Utils import utils_api_jira, utils
from ..models.stories import Stories


def versions_list(request):
    selected = "versions"
    list_versions = Versions.objects.all()
    # Pagination 10 per pages
    paginator = Paginator(list_versions.order_by('name'), 10)
    try:
        page = request.GET.get("page")
        if not page:
            page = 1
        list_versions = paginator.page(page)
    except EmptyPage:
        list_versions = paginator.page(paginator.num_pages())

    return render(request, 'versions/versions_list.html', locals())


def version_detail(request, pk):
    selected = "versions"
    version = Versions.objects.get(id=pk)
    list_task = Tasks.objects.filter(version=version.name)
    tasks_done = list_task.filter(status="Done")
    tasks_todo = list_task.filter(status="To Do")
    tasks_val = list_task.filter(status="validated on test")
    tasks_progress = list_task.filter(status="In Progress")
    tasks_backlog = list_task.filter(status="BACKLOG")
    tasks_review = list_task.filter(status="CODE REVIEW")
    label_tasks = ["Done", "To Do", "validated on test", "In Progress", "Backlog", "Code review"]
    data_tasks = [len(tasks_done), len(tasks_todo), len(tasks_val), len(tasks_progress),len(tasks_backlog),len(tasks_review)]

    list_stories = Stories.objects.filter(version=version.name)
    stories_done = list_stories.filter(status="Done")
    stories_progress = list_stories.filter(status="In Progress")
    stories_todo = list_stories.filter(status="To Do")
    stories_backlog = list_stories.filter(status="BACKLOG")
    stories_deploy = list_stories.filter(status="READY TO DEPLOY")
    stories_recette = list_stories.filter(status="READY ON RECETTE")
    data_stories = [len(stories_done), len(stories_progress), len(stories_todo), len(stories_backlog),
                    len(stories_deploy), len(stories_recette)]
    label_stories = ["Done", "In Progress", "To do", "Backlog", "Ready to deploy","Ready on recette"]
    return render(request, 'versions/version_detail.html', locals())


def updates_versions(request, pk):
    version = Versions.objects.get(id=pk)
    print('Update version', version.name)
    list_stories = utils_api_jira.get_all_issue_from_version(version.name)
    first_sprint = None
    last_sprint = None
    version_estimation = 0
    version_estimation_done = 0
    nb_bugs = 0
    nb_story = 0
    for stories in list_stories:
        stories_type = stories['fields']['issuetype']['name']
        if stories_type == 'Story':
            nb_story = nb_story + 1
        else:
            nb_bugs = nb_bugs + 1
        # Sprint
        sprint = utils.get_last_sprint_issue(stories)
        if str(sprint['sprint']) != '':
            if first_sprint is None:
                first_sprint = sprint
            else:
                first_sprint = utils.get_first_sprint(first_sprint, sprint)

            if last_sprint is None:
                last_sprint = sprint
            else:
                last_sprint = utils.get_last_sprint(last_sprint, sprint)

        estimations = utils_api_jira.get_story_estimations(stories)
        version_estimation = version_estimation + estimations['estimation']
        version_estimation_done = version_estimation_done + estimations['estimation_done']

    version.stories = nb_story
    version.bugs = nb_bugs
    version.first_sprint = first_sprint['sprint']
    version.start_date_dev = parse_datetime(str(first_sprint['start_date']))
    version.last_sprint = last_sprint['sprint']
    version.end_date_dev = parse_datetime(str(last_sprint['end_date']))
    version.estimation = version_estimation
    version.estimation_remaining = version_estimation - version_estimation_done
    version.save()

    return redirect('versions')
