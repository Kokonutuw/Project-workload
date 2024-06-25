from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage
from django.shortcuts import render

from ..models.projects_customers import ProjectsCustomers


def projects_customers_list(request):
    selected = "projects_customers"
    list_projects_customers = ProjectsCustomers.objects.all()
    # Pagination 10 per pages
    paginator = Paginator(list_projects_customers.order_by('stories').reverse(), 10)
    try:
        page = request.GET.get("page")
        if not page:
            page = 1
        list_projects_customers = paginator.page(page)
    except EmptyPage:
        list_projects_customers = paginator.page(paginator.num_pages())

    return render(request, 'projects_customers/projects_customers_list.html', locals())
