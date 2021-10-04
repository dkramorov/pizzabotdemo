import json

from django.contrib.auth.models import AnonymousUser, User
from django.test import TestCase, RequestFactory

from .views import index, prepare_user_state_machine, save_user_state_machine
from .telegram import TelegramMessage
from .pizza_state_machine import PizzaStateMachine
from .models import PizzaOrder

class SimpleTest(TestCase):
    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()

    def test_details(self):
        # Create an instance of a GET request.
        request = self.factory.get("/")
        request.user = AnonymousUser()

        # Test my_view() as if it were deployed at /customer/details
        response = index(request)
        self.assertEqual(response.status_code, 200)

class TelegramTest(TestCase):

    def test_pase_message(self):
        messages = [
            b'{"update_id":367768509,\n"message":{"message_id":8,"from":{"id":568445508,"is_bot":false,"first_name":"Den","last_name":"Kramorov","username":"j_cker","language_code":"ru"},"chat":{"id":568445508,"first_name":"Den","last_name":"Kramorov","username":"j_cker","type":"private"},"date":1633320628,"text":"test 5"}}',
            b'{"update_id":367768510,\n"message":{"message_id":9,"from":{"id":1866821302,"is_bot":false,"first_name":"\\u0418\\u043d\\u043d\\u0430","last_name":"\\u042f\\u0440\\u043e\\u0441\\u043b\\u0430\\u0432\\u0446\\u0435\\u0432\\u0430","language_code":"ru"},"chat":{"id":1866821302,"first_name":"\\u0418\\u043d\\u043d\\u0430","last_name":"\\u042f\\u0440\\u043e\\u0441\\u043b\\u0430\\u0432\\u0446\\u0435\\u0432\\u0430","type":"private"},"date":1633320842,"text":"/start","entities":[{"offset":0,"length":6,"type":"bot_command"}]}}',
            b'{"update_id":367768511,\n"message":{"message_id":10,"from":{"id":1866821302,"is_bot":false,"first_name":"\\u0418\\u043d\\u043d\\u0430","last_name":"\\u042f\\u0440\\u043e\\u0441\\u043b\\u0430\\u0432\\u0446\\u0435\\u0432\\u0430","language_code":"ru"},"chat":{"id":1866821302,"first_name":"\\u0418\\u043d\\u043d\\u0430","last_name":"\\u042f\\u0440\\u043e\\u0441\\u043b\\u0430\\u0432\\u0446\\u0435\\u0432\\u0430","type":"private"},"date":1633320846,"text":"Gggg"}}',
        ]
        for body_bytes in messages:
            json_msg = TelegramMessage(body_bytes)
            self.assertTrue(json_msg.error is None)
            self.assertTrue(json_msg.text in ('test 5', '/start', 'Gggg'))


class PizzaOrderTest(TestCase):

    def test_save_order(self):
        chat_id = 1
        state_machine = PizzaStateMachine()
        new_state = prepare_user_state_machine(chat_id=chat_id)
        save_user_state_machine(chat_id=chat_id, state_machine=state_machine)
        old_state = prepare_user_state_machine(chat_id=chat_id)
        self.assertTrue(new_state.state == old_state.state)
        self.assertTrue(PizzaOrder.objects.filter(chat_id=chat_id).count() > 0)
        state_machine.ask_pizza_size('маленькая')

        save_user_state_machine(chat_id=chat_id, state_machine=state_machine)
        order = PizzaOrder.objects.filter(chat_id=chat_id).first()
        params = json.loads(order.cur_state)
        self.assertTrue(state_machine.get_params()['state'] == params['state'])

    def test_complete_order(self):
        chat_id = 2
        state_machine = PizzaStateMachine()
        state = prepare_user_state_machine(chat_id=chat_id)
        save_user_state_machine(chat_id=chat_id, state_machine=state_machine)
        state_machine.ask_pizza_size('БольШАЯ')
        save_user_state_machine(chat_id=chat_id, state_machine=state_machine)
        order = PizzaOrder.objects.filter(chat_id=chat_id, in_progress=True).first()
        params = json.loads(order.cur_state)
        self.assertTrue(state_machine.get_params()['state'] == params['state'])

        state_machine.ask_payment_method('нал')
        save_user_state_machine(chat_id=chat_id, state_machine=state_machine)
        order = PizzaOrder.objects.filter(chat_id=chat_id, in_progress=True).first()
        params = json.loads(order.cur_state)
        self.assertTrue(state_machine.get_params()['state'] == params['state'])
        self.assertTrue(state_machine.get_params()['params']['selected_pizza_size'] == params['params']['selected_pizza_size'])
        self.assertTrue(state_machine.get_params()['params']['selected_payment_method'] == params['params']['selected_payment_method'])

        state_machine.ask_confirmation('дА')
        save_user_state_machine(chat_id=chat_id, state_machine=state_machine)
        order = PizzaOrder.objects.filter(pk=order.id).first()
        self.assertTrue(order.in_progress==False)


class PizzaStateMachineTest(TestCase):

    def test_initial_state(self):
        test_machine = PizzaStateMachine(initial_state = 'thanks_for_order')
        self.assertEqual(test_machine.state, 'thanks_for_order')

    def test_repeat_steps(self):
        chat_id = 3
        state_machine = PizzaStateMachine()
        state = prepare_user_state_machine(chat_id=chat_id)
        save_user_state_machine(chat_id=chat_id, state_machine=state_machine)

        state_machine.ask_pizza_size('хз')
        save_user_state_machine(chat_id=chat_id, state_machine=state_machine)
        self.assertTrue(state_machine.get_params()['state'] == 'select_pizza_size')

        state_machine.ask_pizza_size('МаленькуЮ')
        save_user_state_machine(chat_id=chat_id, state_machine=state_machine)
        order = PizzaOrder.objects.filter(chat_id=chat_id, in_progress=True).first()
        params = json.loads(order.cur_state)
        self.assertTrue(state_machine.get_params()['state'] == params['state'])
        self.assertTrue(state_machine.get_params()['params']['selected_pizza_size'] == params['params']['selected_pizza_size'])

        state_machine.ask_payment_method('БенаЛ')
        save_user_state_machine(chat_id=chat_id, state_machine=state_machine)
        order = PizzaOrder.objects.filter(chat_id=chat_id, in_progress=True).first()
        params = json.loads(order.cur_state)
        self.assertTrue(state_machine.get_params()['state'] == params['state'])
        self.assertTrue(state_machine.get_params()['params']['selected_pizza_size'] == params['params']['selected_pizza_size'])
        self.assertTrue(state_machine.get_params()['params']['selected_payment_method'] == params['params']['selected_payment_method'])
        self.assertTrue(state_machine.get_params()['params']['selected_payment_method'] == 'БенаЛ')

        state_machine.ask_confirmation('хз')
        save_user_state_machine(chat_id=chat_id, state_machine=state_machine)
        order = PizzaOrder.objects.filter(pk=order.id).first()
        self.assertTrue(order.in_progress==True)
        self.assertTrue(state_machine.get_params()['state'] == 'select_pizza_size')

    def test_complete_steps(self):
        chat_id = 3
        state_machine = PizzaStateMachine()
        state = prepare_user_state_machine(chat_id=chat_id)
        save_user_state_machine(chat_id=chat_id, state_machine=state_machine)

        state_machine.ask_pizza_size('БОЛЬШУЮ')
        save_user_state_machine(chat_id=chat_id, state_machine=state_machine)
        order = PizzaOrder.objects.filter(chat_id=chat_id, in_progress=True).first()
        params = json.loads(order.cur_state)
        self.assertTrue(state_machine.get_params()['state'] == params['state'])
        self.assertTrue(state_machine.get_params()['params']['selected_pizza_size'] == params['params']['selected_pizza_size'])

        state_machine.ask_payment_method('В рассрочку')
        save_user_state_machine(chat_id=chat_id, state_machine=state_machine)
        order = PizzaOrder.objects.filter(chat_id=chat_id, in_progress=True).first()
        params = json.loads(order.cur_state)
        self.assertTrue(state_machine.get_params()['state'] == params['state'])
        self.assertTrue(state_machine.get_params()['params']['selected_pizza_size'] == params['params']['selected_pizza_size'])
        self.assertTrue(state_machine.get_params()['params']['selected_payment_method'] == params['params']['selected_payment_method'])
        self.assertTrue(state_machine.get_params()['params']['selected_payment_method'] == 'В рассрочку')

        state_machine.ask_confirmation('Да')
        save_user_state_machine(chat_id=chat_id, state_machine=state_machine)
        order = PizzaOrder.objects.filter(pk=order.id).first()
        self.assertTrue(order.in_progress==False)
        self.assertTrue(state_machine.get_params()['state'] == 'thanks_for_order')

