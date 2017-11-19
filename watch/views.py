from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from .diagnose import diagnose_twitter

def home(request):
    return render(request, "watch/home.html", {'name': 'jason'})

@csrf_exempt
def help(request):
    if request.method == 'POST':
        # Run diagnostic

        return HttpResponse(request.POST['handle'])
    else:
        return HttpResponse("Sorry, must be a POST.")