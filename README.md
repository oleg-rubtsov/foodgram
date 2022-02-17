## «Продуктовый помощник»: сайт, на котором пользователи будут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Сервис «Список покупок» позволит пользователям создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

Адрес сайта: http://62.84.120.70/recipes

## Технологии:

- Django Rest Framework  
- Python3  
- Docker  
- PostgreSQL  
- React  
- nginx  
- Git  


## Клонирование репозитория и основные моменты:

Клонировать репозиторий:

```sh
git clone https://github.com/oleg-rubtsov/foodgram-project-react.git
```

Шаблон .env:

DB_ENGINE=django.db.backends.postgresql
DB_NAME=test
POSTGRES_USER=test
POSTGRES_PASSWORD=test
DB_HOST=db
DB_PORT=5432

## Запуск проекта 1 способ: 

Cоздать и активировать виртуальное окружение:

```sh
python -m venv venv
source venv/Scripts/activate
```
Перейти в бэкенд проекта:
 
```sh
cd backend/foodgram
```
Установить зависимости из файла requirements.txt:

```
python -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```
Создать файл .env по шаблону.

Выполнить миграции:

```
python manage.py migrate
python manage.py load_ingredients_and_tags --path ./data/
```
Запустить проект:

```
python manage.py runserver
```

## Запуск проекта через Docker (2 способ):
Перейти в infra
```sh
cd infra
```
Создать файл .env по шаблону.

Запустить сборку и запуск контейнера:
```sh
docker-compose build
docker-compose up
```
Миграция, сбор статики и создание супер-пользователя:
```sh
sudo docker exec infra_backend_1 python manage.py migrate
sudo docker exec -it infra_backend_1 python manage.py createsuperuser
```
Заполнение базы тестовыми данными:
```sh
sudo docker exec infra_backend_1 python manage.py load_ingredients_and_tags
```
# Created by:

Oleg Rubtsov  
oleg.rubtsov99@gmail.com  
+7(925)669-06-11  

