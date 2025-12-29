# NotificationService

Сервис для рассылки уведомлений пользователям.
Может быть использован как полноценный сервис, так и как 
микросервис в составе распределенной системы.

## Содержание

- [Установка и запуск](#установка-и-запуск)
- [API](#api)
- [Аутентификация](#аутентификация)
- [Особенности реализации](#особенности-реализации)
- [Тестирование](#тестирование)
- [Разработка](#разработка)

## Установка и запуск

### Требования

- Docker и Docker Compose (для запуска через Docker)
- Python 3.13+ (для локального запуска)

### Запуск через Docker (рекомендуется)

1. Создайте файл `.env` на основе `.env.example`:

   ```bash
   cp .env.example .env
   ```

2. Для тестового запуска в нем уже заполнены все необходимые данные.
   По умолчанию, любая аутентификация (Keycloak, JWT) отключена для 
   простоты использования.


3. Соберите и запустите проект:
   ```bash
   docker compose up --build -d
   ```

4. API доступно по адресу `http://localhost:8000/api/v1/notifications/`

### Локальный запуск (без Docker)

1. Установите зависимости:
   
   С помощью pip:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # На Windows: .venv\Scripts\activate
   python -m pip install -r requirements.txt
   ```
   
   Или с помощью uv:
   ```bash
   uv venv
   source .venv/bin/activate  # На Windows: .venv\Scripts\activate
   uv sync --all-extras
   ```

2. Создайте файл `.env` с настройками.

   ```bash
   cp .env.example .env
   ```

3. Убедитесь, что PostgreSQL и RabbitMQ запущены и доступны


4. Примените миграции:
   ```bash
   cd notification_service
   python manage.py migrate
   ```

5. Запустите Django сервер:
   ```bash
   python manage.py runserver
   ```

6. В отдельных терминалах запустите Celery worker и scheduler:
   ```bash
   # Worker
   celery -A notification_service.config worker
   
   # Scheduler (beat)
   celery -A notification_service.config beat
   ```

## API

### Отправка уведомления

**Endpoint:** `POST /api/v1/notifications/`

**Требования:**
- JWT токен в заголовке `Authorization: Bearer <token>` (если аутентификация включена)
- Scope: `notifications:send`

**Тело запроса:**
```json
{
  "uuid": "string" | int,
  "user_uuid": "string" | int,
  "title": "string",
  "text": "string",
  "type": "email" | "sms" | "push" | "telegram" | null
}
```

**Пример запроса:**
```bash
curl -X POST http://localhost:8000/api/v1/notifications/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-token>" \
  -d '{
    "uuid": 0,
    "user_uuid": 0,
    "title": "Новое уведомление",
    "text": "Текст уведомления",
    "type": "email"
  }'
```

**Ответ:**
```json
{
  "uuid": "00000000-0000-0000-0000-000000000000",
  "was_created": true,
  "status": "PENDING"
}
```

**Коды ответа:**
- `200` - Уведомление уже существует
- `201` - Уведомление успешно создано
- `400` - Ошибка валидации данных
- `401` - Требуется аутентификация
- `403` - Недостаточно прав (отсутствует scope `notifications:send`)

### Типы уведомлений

Сервис поддерживает следующие типы уведомлений:
- `EMAIL` - Email уведомления
- `SMS` - SMS сообщения
- `PUSH` - Push уведомления
- `TELEGRAM` - Telegram сообщения

## Аутентификация

При желании, в сервисе можно включить аутентификацию 
как с помощью Keycloak, так и с помощью токенов, создаваемых вручную.

### Аутентификация с Keycloak

Добавьте или измените в .env следующую переменную:

```
JWT_KEYCLOAK_ENABLED=True
```

По умолчанию в Keycloak создается 3 пользователя: 
**admin**, **user1**, **user2** с паролями, соответствующими логину
(admin:admin, user1:user1, user2:user2). Только пользователь admin 
имеет доступ к рассылке уведомлений (_notifications:send_).
<details>
  <summary>Отправка запроса на получение токена в Keycloak</summary>

  ```bash
    curl --location 'http://localhost:8080/realms/myrealm/protocol/openid-connect/token' \
    --header 'Content-Type: application/x-www-form-urlencoded' \
    --data-urlencode 'grant_type=password' \
    --data-urlencode 'client_id=notification-service' \
    --data-urlencode 'client_secret=dev-secret' \
    --data-urlencode 'username=admin' \
    --data-urlencode 'password=admin'
  ```

</details>

После получения токена используйте его для отправки запросов 
на NotificationService в Authorization хеадере.

```
Authorization: Bearer ey...
```

### Аутентификация с токеном, создаваемым вручную

Для работы в данном режиме, необходимо либо иметь свой микросервис
для создания токенов, либо нужно создавать токены вручную.

Добавьте или измените в .env следующую переменную, и отключите Keycloak:

```
JWT_AUTH_ENABLED=True
JWT_KEYCLOAK_ENABLED=False
```

Для работы сервиса необходимо предоставить ему публичный ключ из пары 
private key - public key, закодированный в base64. Секретный ключ 
должен использоваться для подписывания JWT. Для тестирования
можно использовать следующий публичный ключ:

```
JWT_PUBLIC_KEY=LS0tLS1CRUdJTiBQVUJMSUMgS0VZLS0tLS0KTUlJQ0lqQU5CZ2txaGtpRzl3MEJBUUVGQUFPQ0FnOEFNSUlDQ2dLQ0FnRUE0ZmFuQkVHTHRlMEVDTlJJZlRxbApSUFFzbXhKRkFJWUtrcnpnL1Fpa0lsZnpLK21ZWEdJbU84bmgxMkMxSEh0c2JNbHVMR0dtcWFjQ2NGOFNtQVNiCkUvZGl5dWdoZmJwQ3RuSmlQRTJoMUpWWmFxN0txRGY1eThuckordzZwamhUVmdLYUhneGlLZzhQK3dUczlaekcKaWplckFkelkxRlVMd21talVtdkQrNThxN3Q2S2lEQWVMM0lqT0ZJcVRIZ09UbDdCUmtXM2k5TlVzaS9Od0o5bwpKTHZueGE4ZU8wNHZIRlJXdko2aHh4TGJmRGtlV3l5MUxmUDg5amNIcTYwZ1o5V1VSd2UweEMzejZiZEVsL2tzCnVPbXlrbTdJWVpWeUNDUFVZMmZ2T1JoaitWMFdrZy9vaUhHZW45NXhwQTJVMmQ3Z1lqdVpjLzhPc0FWMk1mWXUKUmRoZmw4TzRucDgxN2RLYW5vU2cydHcwQS9PQkVjQU56azU1ck4wZVMyRFlXejVJb0JSUUtFUFVXV3FMbkhjMQpwMGpkSUFwVTIwcldmQ0R5YVVub0toR05SNUVROTdqY2xLS0hqSUloN2xISjAxb2UvU05GVnNtSFBVRHZ1YTZECllOK0hQVXdtdHFNR3EvcWhjRndxZXJYY01UbnB3N0pXK25seUNFMWF3MzdkekUxSUVKZmI0MGpEbHBNQnhFOFgKaUJ6ckxpQnFPNk9IOGJuNmxDVHF5RVVuY25lRmozVExraHN1eklJZDZDeWNFWmxXM2lldCsrT0d1cWpsNWY3eQpJV1QzeWpWd0RwQ0FDWkNzYnQ3anJ5eVI3djFrVmYvYUpLblRFWHZwTUg3Z08zbXpCcEE5OFV4NHFWYU50QWxBCnZhWW9Na0h0QWhFcXdKMUQ3dDJ0NmpNQ0F3RUFBUT09Ci0tLS0tRU5EIFBVQkxJQyBLRVktLS0tLQo=
```

И следующий токен, который подписан на очень долгое время:

```
eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJhdXRoLXByb3ZpZGVyIiwic3ViIjoiMDAwMDAwMDAtMDAwMC0wMDAwLTAwMDAtMDAwMDAwMDAwMDAwIiwiYXVkIjoibm90aWZpY2F0aW9uLXNlcnZpY2UiLCJpYXQiOjE3NjY5ODYxMTUsImV4cCI6MTA0MDY5ODYxMTUsImp0aSI6ImE3YmUzODRlLTBmMjktNGJhZi05YWMyLTQxMzE3MzBhOWM3OCIsInNjb3BlIjoibm90aWZpY2F0aW9uczpzZW5kIn0.oUEMUJtT-k-U4fce4o-ZVTrbXvF6t4S0COUN7TVa5MfJ23L5MWnArgseCTcqS9lIYNZHKeYXNbyuzu8-L6ha92gycwi_BnSbR6UAlTgzuxmIDC_y47lSGRP3j4ov40t9S4-Q4nxrPNaKPvnWc8sLwPzOBYFzZ3SfKERSyHygyjOBI2TOukpJupqBfdV6rrZDbi7XyBMhcZJ5B1LpWxS5DBShhKZmnQcI-vmqyo7458jibRFasXI3XknBABT6pWuQ5bfQhBkAkcIKwZzfbctXeZoX3FR6fC8JJ95hXDEJxQMx-cp9uVVdgc0ohuK6tB5FLkdNcpLDhm5KCT_MN6yxW3gQc7r4vW8Ydgap3Ul7nOs2wn_nKF6OxkOvz0pSsbg9XaLY3MZd2DNliRVjEq8CHgykqq7Wdl2yC3ej3Pv2VEuhVbLL7auzRDluF7uBeXF8MQcO1NJYoCy8Kr2jiSw553QbzAFxFjGs0ZC8yEVAY2y68669k9swBjaVzJ08sHEmSmlI-4jBFqP82zUGSbDilcnCMbJXQenAW__sXy-YJCGfM06EfyljDp5G2rtfDkt15vfyFnwedkVTbMNahGqz0WNly9MS74iMItooPu2j8InkQcz_RCmgEqsZTb__ZQ_qP507U1HYlumc6mBCV4BQzsiioMabbkbjOEmTwFVs5Uc
```

## Тестирование

Для запуска тестов используйте pytest:

```bash
# Запуск всех тестов
pytest

# Запуск с покрытием кода
pytest --cov=notification_service --cov-report=html

# Запуск конкретного теста
pytest tests/test_adapters_api_views.py
```

Тесты используют отдельную тестовую базу данных и не требуют запущенных сервисов (RabbitMQ, Keycloak и т.д.).

## Особенности реализации

### Асинхронная отправка уведомлений

Отправка уведомлений происходит воркером, который на постоянной 
основе следит за новыми уведомлениями в БД и, при появлении нового, 
создает лок на строку и отправляет его. Это дает возможность
динамически менять количество воркеров, и тем самым ускорять отправку 
уведомлений при больших нагрузках.

### UserProvider

Сервису необходимо откуда-то получать информацию о доступных каналах
нотификации пользователя. По умолчанию, используется локальный список
пользователей: в коде создано несколько тестовых юзеров с id 0 и 1,
у которых есть разные каналы. Они хранятся в 
`notification_service.adapters.user_provider.local.LocalUserProvider`.

Так же реализована возможность использовать Keycloak для 
получения каналов пользователя 
(`notification_service.adapters.user_provider.keycloak.KeycloakUserProvider`).
При запуске Keycloak создаются 2 тестовых пользователя (user1, user2)
с разными доступными каналами нотификации, но из-за особенностей Keycloak
получить id пользователей можно только после первого запуска сервиса.

Для работы `KeycloakUserProvider` необходимо заполнить логин и пароль
сервисного пользователя, у которого есть доступ к чтению пользователей:

```
# For UserProvider (keycloak admin is needed)
JWT_KEYCLOAK_ADMIN_LOGIN=admin
JWT_KEYCLOAK_ADMIN_PASSWORD=admin
```

### Sidenote

В проекте намеренно упрощены или упущены некоторые особенности.
Например:

1. Keycloak настроен очень примитивно. В нем есть тот самый базовый
   минимум, необходимый для работы сервиса, но использовать его в 
   продакшене **крайне не рекомендуется**.
2. Создание токенов вручную намеренно упущено в сервисе, 
   потому как это размывает его круг обязанностей (он должен отвечать 
   только за рассылку уведомлений, но не за аутентификацию пользователей).
3. Индексы добавлены только на минимально нужные для работы поля. Если
   бизнесу нужны будут дополнительные фильтры / более сложные запросы,
   имеет смысл создать новую миграцию и добавить необходимые индексы.

## Разработка

### Структура проекта

Проект следует принципам Clean Architecture (DDD + Hexagonal):

- `domain/` - Доменные сущности и перечисления
- `application/` - Use cases, DTOs и порты (интерфейсы)
- `adapters/` - Реализации портов (API, БД, workers, user providers)
- `config/` - Конфигурация Django, Celery, Keycloak

### Создание миграций

```bash
cd notification_service
python manage.py makemigrations
python manage.py migrate
```

### Запуск в режиме разработки

Для разработки рекомендуется использовать локальный запуск без Docker:

1. Установите зависимости (см. раздел [Локальный запуск (без Docker)](#локальный-запуск-без-docker))
2. Запустите необходимые сервисы через Docker:
   ```bash
   docker compose up -d
   docker compose stop notification_service
   ```
3. Запустите Django сервер с автоперезагрузкой:
   ```bash
   python manage.py runserver
   ```

### Логирование

Сервис использует `loguru` для логирования. Логи выводятся в консоль и могут быть настроены через переменные окружения.