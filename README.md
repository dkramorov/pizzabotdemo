Демонстрация тестового задания телеграм бота с использованием машины состояний

## Требования
1.	Бот должен поддерживать работу только с телеграммом - но вы должны учесть возможность подключения другого средства коммуникации (фб, вк, скайп)
2.	Бот должен обрабатывать следующий диалог
  2.1.	Какую вы хотите пиццу? Большую или маленькую?
  2.2.	Большую
  2.3.	Как вы будете платить?
  2.4.	Наличкой
  2.5.	Вы хотите большую пиццу, оплата - наличкой?
  2.6.	Да
  2.7.	Спасибо за заказ
3.	Для стейт машины использовать https://github.com/pytransitions/transitions
4.	Добавить тесты для диалога
5.	Выложить бота на хероку и подключить его к телеграмму
          https://devcenter.heroku.com/articles/getting-started-with-python#deploy-the-app
6.	Код выложить на гитхаб или хероку


# Python: Getting Started

A barebones Django app, which can easily be deployed to Heroku.

This application supports the [Getting Started with Python on Heroku](https://devcenter.heroku.com/articles/getting-started-with-python) article - check it out.

## Running Locally

Make sure you have Python 3.9 [installed locally](https://docs.python-guide.org/starting/installation/). To push to Heroku, you'll need to install the [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli), as well as [Postgres](https://devcenter.heroku.com/articles/heroku-postgresql#local-setup).

```sh
$ git clone https://github.com/heroku/python-getting-started.git
$ cd python-getting-started

$ python3 -m venv getting-started
$ pip install -r requirements.txt

$ createdb python_getting_started

$ python manage.py migrate
$ python manage.py collectstatic

$ heroku local
```

Your app should now be running on [localhost:5000](http://localhost:5000/).

## Deploying to Heroku

```sh
$ heroku create
$ git push heroku main

$ heroku run python manage.py migrate
$ heroku open
```
or

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

## Documentation

For more information about using Python on Heroku, see these Dev Center articles:

- [Python on Heroku](https://devcenter.heroku.com/categories/python)
