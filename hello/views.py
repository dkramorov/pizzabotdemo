import os
import requests
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .telegram import TelegramBot
from .models import Greeting

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
TELEGRAM_PROXY = os.environ.get('TELEGRAM_PROXY')

# Create your views here.
def index(request):
    r = requests.get('http://httpbin.org/status/418')
    print(r.text)
    return HttpResponse('<pre>' + r.text + '</pre>')
    # return HttpResponse('Hello from Python!')
    #return render(request, "index.html")


def db(request):
    greeting = Greeting()
    greeting.save()
    greetings = Greeting.objects.all()
    return render(request, "db.html", {"greetings": greetings})

@csrf_exempt
def pizza_webhook(request):
    """Webhook endpoint for pizza bot"""
    bot = TelegramBot(token=TELEGRAM_TOKEN,
                      chat_id=TELEGRAM_CHAT_ID,
                      proxy=TELEGRAM_PROXY)
    result = {'result': 'success'}
    body = request.body.decode('utf-8')
    if body:
        bot.send_message('body: ' + body)
    post_items = ['%s:%s' % (key, value) for key, value in request.POST.items()]
    if post_items:
        bot.send_message('post_items: ' + post_items.join('\n'))
    return JsonResponse(result, safe=False)

