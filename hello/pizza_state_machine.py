#!/usr/bin/env python

from transitions import Machine
from enum import Enum

class PizzaStateMachine(object):
    """Необходимо написать небольшого чат-бота использую стейт-машину
       Требования
       1.	Бот должен поддерживать работу только с телеграммом - но вы должны учесть возможность подключения другого средства коммуникации (фб, вк, скайп)
       2.	Бот должен обрабатывать следующий диалог
         1.	Какую вы хотите пиццу? Большую или маленькую?
         2.	Большую
         3.	Как вы будете платить?
         4.	Наличкой
         5.	Вы хотите большую пиццу, оплата - наличкой?
         6.	Да
         7.	Спасибо за заказ
       3.	Для стейт машины использовать https://github.com/pytransitions/transitions
       4.	Добавить тесты для диалога
       5.	Выложить бота на хероку и подключить его к телеграмму
          https://devcenter.heroku.com/articles/getting-started-with-python#deploy-the-app
       6.	Код выложить на гитхаб или хероку
       7.	Примерный срок выполнения - 2 дня
    """
    states = [
        'select_pizza_size',
        'select_payment_method',
        'confirm_order',
        'thanks_for_order',
    ]

    def __init__(self, initial_state: str = 'select_pizza_size'):
        self.machine = Machine(model=self,
                               states=PizzaStateMachine.states,
                               initial=initial_state)
        self.selected_pizza_size = ''
        self.selected_payment_method = ''

        self.machine.add_transition(trigger='set_pizza_size',
                                    source='select_pizza_size',
                                    dest='select_payment_method')
        self.machine.add_transition(trigger='set_payment_method',
                                    source='select_payment_method',
                                    dest='confirm_order')
        self.machine.add_transition(trigger='set_order',
                                    source='confirm_order',
                                    dest='thanks_for_order')
        self.machine.add_transition(trigger='restart',
                                    source='*',
                                    dest='select_pizza_size',
                                    before='reset')

    def get_params(self):
        """Get params of current state"""
        return {
            'state': self.state,
            'params': {
                'selected_pizza_size': self.selected_pizza_size,
                'selected_payment_method': self.selected_payment_method,
            }
        }

    def ask_pizza_size(self, size: str):
        """Validate size of pizza
           :param size: selected size of pizza
        """
        next_question = 'Как вы будете платить?'
        repeat_question = 'Какую вы хотите пиццу? Большую или маленькую?'
        if not size:
            return repeat_question
        if size.lower() in ('маленькая', 'большая', 'маленькую', 'большую'):
            self.selected_pizza_size = size
            self.trigger('set_pizza_size')
            return next_question
        return repeat_question

    def ask_payment_method(self, payment_method: str):
        """Validate payment method
           :param size: selected size of pizza
        """
        next_question = 'Вы хотите %s пиццу' % self.selected_pizza_size
        repeat_question = 'Как вы будете платить?'
        if not payment_method:
            return repeat_question
        self.selected_payment_method = payment_method
        self.trigger('set_payment_method')
        return '%s, оплата %s?' % (next_question, payment_method)

    def ask_confirmation(self, confirmation: str):
        """Ask confirmation
           :param size: yes/no answer
        """
        next_question = 'Спасибо за заказ'
        repeat_question = 'Какую вы хотите пиццу? Большую или маленькую?'
        if not confirmation.lower() in ('y', 'yes', 'д', 'да'):
            self.trigger('restart')
            return repeat_question
        self.trigger('set_order')
        return next_question

    def reset(self):
        """Reset stored data"""
        self.selected_pizza_size = ''
        self.selected_payment_method = ''
