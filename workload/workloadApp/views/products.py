from django.core.paginator import Paginator, EmptyPage
from django.shortcuts import render

from ..models.products import Products


def products_list(request):
    selected = "products"
    list_products = Products.objects.all()
    # Pagination 10 per pages
    paginator = Paginator(list_products.order_by('key'), 10)
    try:
        page = request.GET.get("page")
        if not page:
            page = 1
        list_products = paginator.page(page)
    except EmptyPage:
        list_products = paginator.page(paginator.num_pages())

    return render(request, 'products/products_list.html', locals())
