from django.core.paginator import Paginator, EmptyPage
from django.shortcuts import render

from ..models.epic import Epic


def epics_list(request):
    selected = "epics"
    list_epics = Epic.objects.all()
    # Pagination 10 per pages
    paginator = Paginator(list_epics.order_by('issue_key'), 10)
    try:
        page = request.GET.get("page")
        if not page:
            page = 1
        list_epics = paginator.page(page)
    except EmptyPage:
        list_epics = paginator.page(paginator.num_pages())
    return render(request, 'epics/epics_list.html', locals())
