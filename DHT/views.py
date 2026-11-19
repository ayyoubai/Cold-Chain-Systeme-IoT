from django.shortcuts import render
from django.http import HttpResponse, FileResponse
import os
from django.shortcuts import render

def dashboard(request):
    return render(request, 'dashboard.html')


def test(request):
    return HttpResponse("Je suis Zakaria")


def dashboard(request):
    file_path = os.path.join(
        os.path.dirname(__file__),
        'dashboard.html'
    )

    return FileResponse(open(file_path, 'rb'))