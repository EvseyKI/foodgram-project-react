# Cервис Foodgram - продуктовый помощник

## Описание

Проект «Фудграм» — сайт, на котором пользователи могут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Пользователям сайта также доступен сервис «Список покупок». Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд. 

Проект доступен по [адресу](http://158.160.76.203/)

## Установка

1. Клонируйте репозиторий на свой компьютер:

    ```
    git clone https://github.com/devlili/foodgram-project-react.git
    ```
    ```
    cd foodgram-project-react
    ```
2. Создайте файл .env в папке infra и заполните его своими данными. Перечень данных указан в файле .env.example.

3. Находясь в папке infra, выполните команду ```docker-compose up```  
Документация к API доступна по адресу http://localhost/api/docs/ 

### Создание Docker-образов

1.  Создаём образы для установки на сервер. Замените username на ваш логин на DockerHub:

    ```
    cd ..
    docker build -t username/foodgram_backend backend/
    docker build -t username/foodgram_frontend rontend/
    ```

2. Загрузите образы на DockerHub:

    ```
    docker push username/foodgram_frontend
    docker push username/foodgram_backend
    ```

## Автор

    Evsey Kirichkov
    Beginner python developer