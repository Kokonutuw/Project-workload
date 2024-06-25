from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage
from django.shortcuts import render

from ..models.tasks import Tasks

from management.Utils import utils_api_jira as utils_api_jira


@login_required
def tasks_list(request):
    selected = "tasks"
    tasks_list = Tasks.objects.all()
    paginator = Paginator(tasks_list.order_by('key'), 10)
    try:
        page = request.GET.get("page")
        if not page:
            page = 1
        tasks_list = paginator.page(page)
    except EmptyPage:
        tasks_list = paginator.page(paginator.num_pages())

    task_key = "TUVBI-87"
    issue = utils_api_jira.get_task(task_key)
    issue = utils_api_jira.get_task_assignation(issue)
    return render(request, 'tasks/tasks_list.html', locals())


def update_tasks(request, pk):
    print('update tasks')
    list_issues = utils_api_jira.get_all_issue_by_tasks(Tasks.objects.get(id=pk).name)

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
