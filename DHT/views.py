import os
from django.http import HttpResponse, FileResponse


def test(request):
    return HttpResponse("Je suis Zakaria")


def dashboard(request):
    file_path = os.path.join(
        os.path.dirname(__file__),
        'static', 'DHT', 'dashboard.html'
    )
    return FileResponse(open(file_path, 'rb'), content_type='text/html')