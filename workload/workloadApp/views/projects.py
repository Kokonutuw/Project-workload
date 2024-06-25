from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage
from django.shortcuts import render
import datetime

from django.db.models import Sum, F
from django.shortcuts import render

from ..models.projects import Projects


def projects_list(request):
    selected = "projects"
    list_projects = Projects.objects.all()
    # Pagination 10 per pages
    paginator = Paginator(list_projects.order_by('key'), 10)
    try:
        page = request.GET.get("page")
        if not page:
            page = 1
        list_projects = paginator.page(page)
    except EmptyPage:
        list_projects = paginator.page(paginator.num_pages())
    return render(request, 'projects/projects_list.html', locals())
