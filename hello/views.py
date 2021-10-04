import os
import json
import requests
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .pizza_state_machine import PizzaStateMachine
from .telegram import TelegramBot, TelegramMessage
from .models import Greeting, PizzaOrder

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

def prepare_user_state_machine(chat_id: int):
    """Prepare state machine for work
       :param chat_id: user chat id
    """
    order = PizzaOrder.objects.filter(chat_id=chat_id, in_progress=1).first()
    if not order:
        state_machine = PizzaStateMachine()
    else:
        cur_state = json.loads(order.cur_state)
        state_machine = PizzaStateMachine(cur_state['state'])
        for key, value in cur_state['params'].items():
            setattr(state_machine, key, value)
    return state_machine

def save_user_state_machine(chat_id: int, state_machine: PizzaStateMachine):
    """Prepare state machine for work
       :param chat_id: chat id for user
       :param state_machine: instance PizzaStateMachine
    """
    order = PizzaOrder.objects.filter(chat_id=chat_id, in_progress=1).first()
    if not order:
        order = PizzaOrder(chat_id=chat_id, in_progress=1)
    order.cur_state = json.dumps(state_machine.get_params())
    order.save()

def pizza_order_dialog(msg: TelegramMessage, bot: TelegramBot):
    """Dialog with user
       :param state_machine: instance of PizzaStateMachine
       :param bot: Telegram bot instance
    """
    state_machine = prepare_user_state_machine(msg)

    question = state_machine.ask_pizza_size(msg.text)
    if state_machine.state == 'select_pizza_size':
        pass
    elif state_machine.state == 'select_payment_method':
        question = state_machine.ask_payment_method(msg.text)
    elif state_machine.state == 'thanks_for_order':
        pass
    else:
        pass
    question += ' -> %s' % state_machine.state
    bot.send_message(question, msg.chat_id)
    save_user_state_machine(msg.chat_id, state_machine)

@csrf_exempt
def pizza_webhook(request):
    """Webhook endpoint for pizza bot"""
    bot = TelegramBot(token=TELEGRAM_TOKEN,
                      chat_id=TELEGRAM_CHAT_ID,
                      proxy=TELEGRAM_PROXY)
    result = {'result': 'success'}
    body = request.body.decode('utf-8')
    if body:
        msg = TelegramMessage(request.body)
        if msg.error:
            bot.send_message(msg.error)
        else:
            bot.send_message('%s' % msg.text, msg.chat_id)
            #pizza_order_dialog(msg, bot)
    return JsonResponse(result, safe=False)

