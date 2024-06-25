from django.core.paginator import Paginator, EmptyPage
from django.shortcuts import render

from ..models.stories_epic import Stories_epic


def epics_list(request):
    selected = "epics"
    list_epics_stories = Stories_epic.objects.all()
    # Pagination 10 per pages
    paginator = Paginator(list_epics_stories.order_by('key'), 10)
    try:
        page = request.GET.get("page")
        if not page:
            page = 1
        list_epics_stories = paginator.page(page)
    except EmptyPage:
        list_epics_stories = paginator.page(paginator.num_pages())
    return render(request, 'epic_stories/epic_stories_list.html', locals())
