# API к игре Black Jack

______
В данном модуле реализованы:

* Api к игре:
    * Aiohttp
    * PostgresSQL
____
### Запуск через docker-compose:
При первом запуске в Docker контейнере:
 - Создаем файл `.env` по примеру [`.env_example`](.env_example)
 - Запускаем контейнер:

```docker-compose up --build```
 
 - Входим в контейнер

```docker exec -it bj bash ```  
 - Выполняем:

```alembic upgrade head```

### Запуск на локальной машине, под OC LINUX:
При первом запуске:
Подразумевается что у вас установлена БД PostgresSQL
 - Создаем файл `.env` по примеру [`.env_example`](.env_example)
 - ```sudo su - postgres```
Вводим пароль от "postgres"

   ```psql```
- Создаем пользователя 
  
  ```create user POSTGRES__USER with password 'POSTGRES__PASSWORD';```

   - POSTGRES__USER - заменяем на одноименное значение из `.env`
   - POSTGRES__PASSWORD - заменяем на одноименное значение из `.env`
- Создаем БД

   - ```create database POSTGRES__DB;```
     - POSTGRES__DB - заменяем на одноименное значение из `.env`
- Назначаем права пользователю которого недавно создали:

  ```grant all privileges on all tables in schema public to POSTGRES__USER;```
   - POSTGRES__USER - заменяем на одноименное значение из `.env`
- Выходим:
  - ```\q```
  - ```exit```
 - Переходим в каталог (папку) [`blackJack`](blackJack)

    ```cd blackJack```
 - Устанавливаем миграцию:
   ```alembic upgrade head```
___

вызов:
- http://localhost:8000/docs - api swagger
- пояснения PORT=`8000` - этот порт задается в [`.env_example`](.env_example)
_____
