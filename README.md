## Проект Foodgram

Foodgram - продуктовый помощник с базой кулинарных рецептов. Позволяет публиковать рецепты, сохранять избранные, а также формировать список покупок для выбранных рецептов. Можно подписываться на любимых авторов.

Проект доступен по адресу https://nikitkosss.hopto.org

### Технологии:

Python, Django, Django Rest Framework, Docker, Gunicorn, NGINX, PostgreSQL

## Установка проекта
- Сделайте fork репозитория, затем клонируйте его:
```
git clone git@github.com:Nikitkosss/foodgram-project-react.git
```


- На удаленном сервере создайте папку foodgram/
- На удаленном сервере в папке проекта cоздайте файл .env:

POSTGRES_DB=<Имя_базы_данных>
POSTGRES_USER=<Имя_пользователя_базы_данных>
POSTGRES_PASSWORD=<Пароль_базы_данных>
DB_HOST=db
DB_PORT=5432

SECRET_KEY = 'ваш_secret_key'
ALLOWED_HOSTS = ip_удаленного сервера, доменное имя, 127.0.0.1, localhost
DEBUG = False

- Установка Nginx. Находясь на удалённом сервере, из любой директории выполните команду, затем запустите Nginx:
```
sudo apt install nginx -y 
sudo systemctl start nginx
```
- Перейдите в файл конфигурации nginx и измените его настройки на следующие:
```
nano /etc/nginx/sites-enabled/default
```
```
server {
    server_name server_name <публичный-IP-адрес> <доменное-имя>;
    server_tokens_off;
    client_max_body_size 30M;

    location / {
        proxy_set_header Host $http_host;
        proxy_pass http://127.0.0.1:8000;
    }

}
```
- Перезарузите Nginx:
```
sudo nginx -t
sudo systemctl reload nginx
```
- Откройте порты для фаервола и активируйте его:
```
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw enable
```
- (Опционально) Получите SSL-сертификат для вашего доменного имени с помощью Certbot:
```
sudo apt install snapd
sudo snap install core; sudo snap refresh core
sudo snap install --classic certbot
sudo ln -s /snap/bin/certbot /usr/bin/certbot 
sudo certbot --nginx
```

### Автор backend'а:

[Никита Пискунов](https://vk.com/peace_canoff)