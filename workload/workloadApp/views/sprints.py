from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage
from django.shortcuts import render
from django.views.generic import DetailView

from ..models.sprints import Sprints
from ..models.stories import Stories


@login_required
def sprint_list(request):
    selected = "sprints"
    sprints_list = Sprints.objects.all()

    paginator = Paginator(sprints_list.order_by('start_date'), 10)
    try:
        page = request.GET.get("page")
        if not page:
            page = 1
        sprints_list = paginator.page(page)
    except EmptyPage:
        sprints_list = paginator.page(paginator.num_pages())

    return render(request, 'sprints/sprints_list.html', locals())


class SprintDetailView(DetailView):
    model = Sprints
    template_name = 'sprints/sprint_detail.html'
    context_object_name = 'sprint'


def sprint_detail(request, pk):
    selected = "sprints"
    sprint = Sprints.objects.get(id=pk)
    label_sprint_det = ["Workload", "Workload Done", "Workload Left"]
    data_workload = []
    sprint_estimation_done = sprint.estimation - sprint.estimation_remaining
    data_workload.append(sprint.estimation)
    data_workload.append(sprint_estimation_done)
    data_workload.append(sprint.estimation_remaining)

    list_stories = Stories.objects.filter(sprint=sprint.name)
    stories_done = list_stories.filter(status="Done")
    stories_progress = list_stories.filter(status="In Progress")
    stories_todo = list_stories.filter(status="To Do")
    stories_backlog = list_stories.filter(status="BACKLOG")
    stories_deploy = list_stories.filter(status="READY TO DEPLOY")
    stories_recette = list_stories.filter(status="READY ON RECETTE")
    data_stories = [len(stories_done), len(stories_progress), len(stories_todo), len(stories_backlog),
                    len(stories_deploy), len(stories_recette)]
    label_stories = ["Done", "In Progress", "To do", "Backlog", "Ready to deploy", "Ready on recette"]
    return render(request, 'sprints/sprint_detail.html', locals())
