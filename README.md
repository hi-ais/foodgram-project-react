# Дипломный проект FOODGRAM

![workflow](https://github.com/hi-ais/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)
На онлайн-сервисе Foodgramm пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

## Технологии, используемые в проекте:
- Django
- Django REST Framework
- Python
- Nginx
- PostgreSQL
- Docker
- gunicorn
- Yandex.cloud
- GitHubActions

##  Установка
1. Склонируйте репозиторий на Ваш компьютер

`git@github.com:hi-ais/foodgram-project-react.git`

2. Создайте и активируйте виртуальное окружение:

`python -m venv venv`
`source venv/Scripts/activate`
`python -m pip install`

3. Установите зависимости`:

`pip install -r requirements.txt`

4. Установите линтер flake8

`pip install flake8 pep8-naming flake8-broken-line flake8-return flake8-isort`

5. Проверьте код на соответствие стандартам PEP8 и запустите pytest:

`python -m flake8`
`pytest`

##  Подготовка сервера

1. Войдите на свой удаленный сервер в облаке.
2. Остановите службу nginx:

`sudo systemctl stop nginx`

3. Установите Docker:

`sudo apt install docker.io`

4. Установите docker-compose:

`sudo apt-get update`

`sudo apt-get install docker-compose-plugin`

5. Скопируйте файлы docker-compose.yaml и  **директорию** с файлом default.conf из вашего проекта на сервер в home/<ваш_username>/docker-compose.yaml и home/<ваш_username>/nginx/default.conf соответственно:

`scp docker-compose.yaml <USER>@<HOST>`

`scp default.conf <USER>@<HOST>:/nginx/`

6. Создайте файл **.env** и заполните его по примеру:
```
DB_ENGINE=<django.db.backends.postgresql>
DB_NAME=<имя базы данных postgres>
DB_USER=<пользователь бд>
DB_PASSWORD=<пароль>
DB_HOST=<db>
DB_PORT=<5432>
SECRET_KEY=<секретный ключ проекта django>
DEBUG = False
```
## Работа с Workflow
Вам необходимо добавить в Secrets GitHub переменные окружения для работы:
```
DOCKER_PASSWORD=<пароль от DockerHub>
DOCKER_USERNAME=<имя пользователя>
USER=<username для подключения к серверу>
HOST=<IP сервера>
PASSPHRASE=<пароль для сервера, если он установлен>
SSH_KEY=<ваш SSH ключ (для получения команда: cat ~/.ssh/id_rsa)>

```

* Шаги Workflow :*

- Проверка кода на соответствие PEP8
- Сборка и публикация образа бекенда на DockerHub.
- Автоматический деплой на удаленный сервер.

##  Развертывание приложения

1. Необходимо подключиться к серверу.

`ssh <USER>@<HOST>` 
2. Собрать контейнеры с помощью команды

`sudo docker compose up -d --build`

2. Перейдите в запущенный контейнер приложения *backend* командой:

`sudo docker container exec -it <CONTAINER ID> bash`

3. Внутри контейнера необходимо выполнить миграции, подключить статику и создать суперпользователя:

`python manage.py makemigrations`

`python manage.py migrate`

`python manage.py collectstatic --no-input`

`python manage.py createsuperuser`

Проект будет доступен по вашему IP

Документацию API и все эндпоинты можно посмотеть по ссылке:  http://<ваш_ip>/api/docs/
не получается 