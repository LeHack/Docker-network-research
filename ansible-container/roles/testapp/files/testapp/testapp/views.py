from django.http import HttpResponse, JsonResponse


def index(request):
    host = request.get_host()
    return HttpResponse(
        "<html><head><title>" + host + " - Deploy test</title></head><body>"
        + "<img border='0' src='https://www.docker.com/sites/default/files/mono_horizontal_large.png'></img>"
        + "<h1>Deployment complete!</h1>"
        + "<p>Welcome to the test app index site at " + host + "</p>"
        + "</body></html>"
    )

def echo(request):
    return JsonResponse({"ping": 1})
