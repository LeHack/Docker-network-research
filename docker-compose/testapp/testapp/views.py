from django.http import HttpResponse, JsonResponse


def index(request):
    return HttpResponse("<html><head><title>Deploy test</title></head><body><h1>Deployment complete!</h1><p>Welcome to the test app index site.</p></body></html>")

def echo(request):
    return JsonResponse({"ping": 1})