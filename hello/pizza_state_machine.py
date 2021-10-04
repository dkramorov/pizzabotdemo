#!/usr/bin/env python

from transitions import Machine
from enum import Enum

class PizzaStateMachine(object):
    """Необходимо написать небольшого чат-бота использую стейт-машину
       Требования
       1.	Бот должен поддерживать работу только с телеграммом - но вы должны учесть возможность подключения другого средства коммуникации (фб, вк, скайп)
       2.	Бот должен обрабатывать следующий диалог
         1.	Какую вы хотите пиццу?  Большую или маленькую?
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
        'thanks_for_order',
    ]

    def __init__(self):
        self.machine = Machine(model=self,
                               states=PizzaStateMachine.states,
                               initial='select_pizza_size')
        self.selected_pizza_size = ''
        self.selected_payment_method = ''

        self.machine.add_transition(trigger='save_pizza_size',
                                    source='select_pizza_size',
                                    dest='select_payment_method',
                                    after='set_pizza_size')
        self.machine.add_transition(trigger='save_payment_method',
                                    source='select_payment_method',
                                    dest='thanks_for_order',
                                    after='set_payment_method')
        self.machine.add_transition(trigger='restart',
                                    source='*',
                                    dest='select_pizza_size',
                                    before='reset')

    def set_pizza_size(self, size: str):
        """Remember selected pizza size
           :param size: selected pizza size
        """
        self.selected_pizza_size = size

    def set_payment_method(self, payment_method: str):
        """Remember selected payment method
           :param size: selected payment method
        """
        self.selected_payment_method = payment_method

    def reset(self):
        """Reset stored data"""
        self.selected_pizza_size = ''
        self.selected_payment_method = ''