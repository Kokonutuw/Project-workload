from django.shortcuts import render


def index(request):
    selected = "incoming"
    return render(request, "incoming/incoming.html", locals())
