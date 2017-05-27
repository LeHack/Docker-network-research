from django.http import HttpResponse, JsonResponse


def index(request):
    return HttpResponse("Welcome to the test project index site.")

def echo(request):
    return JsonResponse({"ping": 1})