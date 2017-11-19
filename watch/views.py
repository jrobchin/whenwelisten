from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from .diagnose import diagnose_twitter

def home(request):
    username = request.GET.get('username')
    if username == None:
        username = "twitterhandle"
    return render(request, "watch/index.html", {"input_placeholder": username})

def help(request):
    if request.method == 'POST':
        # Run diagnostic
        handle = request.POST['handle'].strip("@")
        print("STARTING DIAGNOSIS FOR:", handle)
        diagnosis, worst_tweet = diagnose_twitter.diagnose_twitter(handle)
        if diagnosis < 0:
            print("NO RESULTS FOR:", handle)
            return HttpResponse("<h1>NO RESULTS FOR USER!!!!</h1>")
        print("FINISHED DIAGNOSIS FOR:", handle)
        return render(request, "watch/help.html", {'username': handle, 'score': int(diagnosis*100), 'worst_tweet': worst_tweet, 'message': diagnose_twitter.generate_message(int(diagnosis*100))})
    else:
        return HttpResponse("<h1>Failed!</h1>")

@csrf_exempt
def send_dm(request):
    print(request.method)
    if request.method == 'POST':
        username = request.GET['username']
        diagnose_twitter.send_response_dm(username)
        return HttpResponse("It worked!") 
    else:
        return HttpResponse("It failed!")