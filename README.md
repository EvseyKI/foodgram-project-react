# Cервис Foodgram - продуктовый помощник

## Описание

Проект «Фудграм» — сайт, на котором пользователи могут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Пользователям сайта также доступен сервис «Список покупок». Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд. 

Проект доступен по [адресу](http://158.160.76.203/)

### Технологии
- Python 3.9
- Django 4.0
- DRF
- PostgreSQL
- Nginx
- gunicorn
- docker
- GitHub Actions

### Примеры запросов
Пример GET-запроса: получаем информацию о рецепте.
GET .../api/recipes/12
```
{
    "id": 12,
    "tags": [
        {
            "id": 3,
            "name": "Завтрак",
            "color": "#FFFF00",
            "slug": "breakfast"
        }
    ],
    "author": {
        "email": "valek@yandex.ru",
        "id": 5,
        "username": "valek",
        "first_name": "Василий",
        "last_name": "Димитров",
        "is_subscribed": false
    },
    "ingredients": [
        {
            "id": 1441,
            "name": "рис",
            "measurement_unit": "г",
            "amount": 300
        },
        {
            "id": 1491,
            "name": "рыба",
            "measurement_unit": "г",
            "amount": 100
        },
        {
            "id": 1138,
            "name": "огурцы",
            "measurement_unit": "г",
            "amount": 200
        }
    ],
    "is_favorited": false,
    "is_in_shopping_cart": false,
    "name": "Онигири",
    "image": "http://158.160.76.203/media/20231017233117.jpeg",
    "text": "Быстро, просто, полезно, оригинально, для всей семьи!",
    "cooking_time": 40
}
```
Пример GET-запроса: получаем ингредиент.
GET .../api/ingredients/991/
```
{
    "id": 991,
    "name": "мед",
    "measurement_unit": "г"
}
```
## Установка

1. Клонируйте репозиторий на свой компьютер:

```
git clone https://github.com/account_name/foodgram-project-react.git
```
```
cd foodgram-project-react
```
2. Создайте файл .env в папке infra и заполните его своими данными.
3. Находясь в папке infra, выполните команду ```docker-compose up```  
Документация к API доступна по адресу http://localhost/api/docs/
4. Выполните миграции, соберите статику. Заполнение ингредиентов работает автоматически при выполнении миграции.
```
docker compose -f docker-compose.yml up -d
docker compose -f docker-compose.yml exec backend python manage.py migrate
docker compose -f docker-compose.yml exec backend python manage.py collectstatic --no-input
```
5. Администратор создается по команде
```
docker compose -f docker-compose.yml exec backend python manage.py createsuperuser
```

## Автор

Evsey Kirichkov
Beginner python developer