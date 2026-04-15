# Интернет-магазин одежды

Лабораторная работа №1 по курсу "Проектирование программного обеспечения интеллектуальных систем"

## Описание предметной области

Программная система моделирует работу интернет-магазина по продаже одежды. Пользователи могут просматривать товары, добавлять их в корзину, оформлять заказы, оплачивать, отслеживать доставку и возвращать товары.

Пользователь может:
- Регистрироваться и входить в систему
- Просматривать каталог товаров
- Искать товары по названию и категории
- Добавлять товары в корзину
- Оформлять заказы с указанием адреса доставки
- Применять промокоды для скидки
- Оплачивать заказы
- Отслеживать статус доставки
- Возвращать заказы
- Оставлять отзывы на товары

## Описание

Проект реализует симуляцию работы интернет-магазина одежды с учётом следующих возможностей:
- Поиск товаров по названию, категории и цене
- Корзина (добавление, удаление, изменение количества)
- Промокоды (скидка до 100%)
- Статусы заказа (ожидает оплаты, оплачен, доставлен, возвращён и др.)
- Статусы доставки (ожидает передачи, в пути, доставлен)
- Отзывы с рейтингом от 1 до 5

## Структура проекта

clothing_store/

├── models.py           # Модели данных

├── exceptions.py      # Пользовательские исключения

├── services.py        # Бизнес-логика

├── cli.py             # Интерфейс командной строки

├── main.py            # Точка входа

├── tests.py           # Unit-тесты

└── README.md

## Описание классов

### Класс User

**Файл:** `models.py`

**Назначение:** Хранение информации о покупателе.

**Атрибуты:**
- `id: str` — уникальный идентификатор
- `email: str` — электронная почта
- `name: str` — имя пользователя
- `password_hash: str` — хеш пароля
- `registered_at: datetime` — дата регистрации

**Методы:**
- `verify_password(plain_password)` — проверяет пароль

### Класс Seller

**Файл:** `models.py`

**Назначение:** Хранение информации о продавце.

**Атрибуты:**
- `id: str` — уникальный идентификатор
- `name: str` — название продавца
- `contact_email: str` — контактный email

### Класс Product

**Файл:** `models.py`

**Назначение:** Хранение информации о товаре.

**Атрибуты:**
- `id: str` — уникальный идентификатор
- `name: str` — название товара
- `description: str` — описание
- `price: float` — цена
- `category: ProductCategory` — категория (MEN, WOMEN, KIDS, ACCESSORIES)
- `seller_id: str` — идентификатор продавца
- `stock: int` — количество на складе
- `created_at: datetime` — дата добавления

**Методы:**
- `reduce_stock(quantity)` — уменьшает количество на складе
- `increase_stock(quantity)` — увеличивает количество на складе

### Класс Cart

**Файл:** `models.py`

**Назначение:** Управление корзиной покупок.

**Атрибуты:**
- `user_id: str` — идентификатор пользователя
- `items: List[CartItem]` — список позиций

**Методы:**
- `add_product(product, quantity)` — добавляет товар
- `remove_product(product_id)` — удаляет товар
- `update_quantity(product_id, quantity)` — изменяет количество
- `clear()` — очищает корзину
- `get_total()` — возвращает общую сумму
- `get_items_count()` — возвращает количество товаров

### Класс Order

**Файл:** `models.py`

**Назначение:** Хранение информации о заказе.

**Атрибуты:**
- `id: str` — уникальный идентификатор
- `user_id: str` — идентификатор пользователя
- `items: List[CartItem]` — список товаров
- `total_amount: float` — общая сумма
- `status: OrderStatus` — статус заказа
- `created_at: datetime` — дата создания
- `payment: Payment` — информация об оплате
- `delivery: Delivery` — информация о доставке

**Методы:**
- `can_pay()` — можно ли оплатить
- `can_cancel()` — можно ли отменить
- `can_return()` — можно ли вернуть

### Класс Payment

**Файл:** `models.py`

**Назначение:** Управление оплатой заказа.

**Атрибуты:**
- `id: str` — уникальный идентификатор
- `order_id: str` — идентификатор заказа
- `amount: float` — сумма платежа
- `status: PaymentStatus` — статус оплаты
- `paid_at: datetime` — дата оплаты

**Методы:**
- `complete()` — завершает оплату

### Класс Delivery

**Файл:** `models.py`

**Назначение:** Управление доставкой заказа.

**Атрибуты:**
- `id: str` — уникальный идентификатор
- `order_id: str` — идентификатор заказа
- `address: str` — адрес доставки
- `status: DeliveryStatus` — статус доставки
- `tracking_number: str` — трек-номер
- `shipped_at: datetime` — дата отправки
- `delivered_at: datetime` — дата доставки

**Методы:**
- `start_delivery(tracking_number)` — начинает доставку
- `mark_delivered()` — отмечает как доставленный

### Класс Review

**Файл:** `models.py`

**Назначение:** Хранение отзывов на товары.

**Атрибуты:**
- `id: str` — уникальный идентификатор
- `product_id: str` — идентификатор товара
- `user_id: str` — идентификатор пользователя
- `rating: int` — оценка (1-5)
- `comment: str` — текст отзыва
- `created_at: datetime` — дата создания

### Класс PromoCode

**Файл:** `models.py`

**Назначение:** Управление промокодами.

**Атрибуты:**
- `id: str` — уникальный идентификатор
- `code: str` — код промокода
- `discount_percent: float` — процент скидки
- `expires_at: datetime` — дата истечения
- `used: bool` — использован ли

**Методы:**
- `apply(amount)` — применяет скидку к сумме

## Перечисления

**ProductCategory:**
- MEN — Мужская одежда
- WOMEN — Женская одежда
- KIDS — Детская одежда
- ACCESSORIES — Аксессуары

**OrderStatus:**
- PENDING — Ожидает оплаты
- PAID — Оплачен
- PROCESSING — В обработке
- SHIPPED — Отправлен
- DELIVERED — Доставлен
- CANCELLED — Отменён
- RETURNED — Возвращён

**DeliveryStatus:**
- AWAITING_PICKUP — Ожидает передачи в доставку
- IN_TRANSIT — В пути
- DELIVERED — Доставлен

**PaymentStatus:**
- PENDING — Ожидает оплаты
- COMPLETED — Оплачено
- FAILED — Ошибка оплаты
- REFUNDED — Возвращено

## Описание сервисов

### StoreService

**Файл:** `services.py`

**Назначение:** Главный сервис, объединяющий всю бизнес-логику.

**Методы аутентификации:**
- `register(email, name, password)` — регистрация пользователя
- `login(email, password)` — вход в систему
- `logout()` — выход из системы

**Методы работы с товарами:**
- `search_products(query, category, min_price, max_price)` — поиск товаров
- `get_product_by_id(product_id)` — получение товара по ID
- `add_product(name, description, price, category, seller_id, stock)` — добавление товара

**Методы работы с корзиной:**
- `add_to_cart(product_id, quantity)` — добавление товара
- `remove_from_cart(product_id)` — удаление товара
- `update_cart_quantity(product_id, quantity)` — изменение количества
- `view_cart()` — просмотр корзины

**Методы работы с заказами:**
- `create_order(address, promo_code)` — создание заказа
- `pay_order(order_id)` — оплата заказа
- `get_user_orders()` — получение заказов пользователя
- `get_order_by_id(order_id)` — получение заказа по ID

**Методы работы с доставкой:**
- `track_delivery(order_id)` — отслеживание доставки
- `update_delivery_status(order_id, status, tracking_number)` — обновление статуса

**Методы работы с возвратами:**
- `request_return(order_id)` — запрос возврата

**Методы работы с отзывами:**
- `add_review(product_id, rating, comment)` — добавление отзыва

**Административные методы:**
- `add_seller(name, contact_email)` — добавление продавца
- `add_promo_code(code, discount_percent, expires_at)` — добавление промокода

## Исключения

**Файл:** `exceptions.py`

Все исключения наследуются от `StoreException`.

**Список исключений:**

- `AuthenticationError` — ошибка аутентификации
- `UserAlreadyExistsError` — пользователь уже существует
- `UserNotFoundError` — пользователь не найден
- `InvalidPasswordError` — неверный пароль
- `NotAuthenticatedError` — пользователь не авторизован
- `ProductNotFoundError` — товар не найден
- `InsufficientStockError` — недостаточно товара на складе
- `ProductNotAvailableError` — товар временно недоступен
- `CartEmptyError` — корзина пуста
- `CartItemNotFoundError` — товар не найден в корзине
- `OrderNotFoundError` — заказ не найден
- `OrderNotBelongToUserError` — заказ не принадлежит пользователю
- `OrderCannotBePaidError` — заказ нельзя оплатить
- `OrderCannotBeCancelledError` — заказ нельзя отменить
- `OrderCannotBeReturnedError` — заказ нельзя вернуть
- `PaymentNotFoundError` — платёж не найден
- `PaymentAlreadyProcessedError` — платёж уже обработан
- `PaymentFailedError` — ошибка оплаты
- `DeliveryNotFoundError` — доставка не найдена
- `DeliveryAlreadyStartedError` — доставка уже начата
- `TrackingNumberRequiredError` — требуется трек-номер
- `InvalidDeliveryStatusError` — некорректный статус доставки
- `PromoCodeNotFoundError` — промокод не найден
- `PromoCodeExpiredError` — срок действия промокода истёк
- `PromoCodeAlreadyUsedError` — промокод уже использован
- `InvalidRatingError` — некорректная оценка
- `InvalidOperationError` — некорректная операция
- `ValidationError` — ошибка валидации
- `DataNotFoundError` — данные не найдены
- `PermissionDeniedError` — недостаточно прав

## CLI интерфейс

**Файл:** `cli.py`, `main.py`

### Доступные команды

- `register <email> <name> <password>` — регистрация
- `login <email> <password>` — вход
- `logout` — выход
- `whoami` — информация о пользователе
- `list` — список всех товаров
- `list <men/women/kids/accessories>` — товары по категории
- `search <текст>` — поиск товаров
- `info <product_id>` — информация о товаре
- `cart` — показать корзину
- `add <product_id> [количество]` — добавить товар
- `remove <product_id>` — удалить товар
- `update <product_id> <количество>` — изменить количество
- `clear` — очистить корзину
- `checkout <адрес> [промокод]` — оформить заказ
- `pay <order_id>` — оплатить заказ
- `orders` — список заказов
- `order <order_id>` — детали заказа
- `track <order_id>` — отследить доставку
- `return <order_id>` — вернуть заказ
- `review <product_id> <оценка> <текст>` — оставить отзыв
- `add_product <название> <цена> <категория> <количество>` — добавить товар
- `add_promo <код> <скидка%> <дней>` — добавить промокод
- `help` — справка
- `exit` — выход

### Пример сессии

guest@store $ register ivan@mail.ru Иван pass123

Пользователь 'Иван' успешно зарегистрирован.

guest@store $ login ivan@mail.ru pass123

Добро пожаловать, Иван!

Иван@store $ list

СПИСОК ТОВАРОВ (5 шт.):
a1b2c3d4 | Футболка хлопковая белая | 1299.99 руб. | Мужская одежда | 25 шт.
e5f6g7h8 | Джинсы скинни синие | 3499.99 руб. | Мужская одежда | 15 шт.
i9j0k1l2 | Платье летнее цветочное | 2799.99 руб. | Женская одежда | 10 шт.

Иван@store $ add a1b2c3d4 2

Товар добавлен в корзину (x2)

Иван@store $ cart

ВАША КОРЗИНА:
Футболка хлопковая белая x2 = 2599.98 руб.
ИТОГО: 2599.98 руб.

Иван@store $ checkout "г. Москва, ул. Ленина 1" WELCOME10

ЗАКАЗ УСПЕШНО ОФОРМЛЕН!
Номер заказа: xyz-789-uvw
Сумма заказа: 2339.98 руб.

Иван@store $ pay xyz-789-uvw

ЗАКАЗ УСПЕШНО ОПЛАЧЕН!

Иван@store $ orders

ВАШИ ЗАКАЗЫ (1 шт.):
xyz-789-uvw | 24.03.2026 16:00 | 2339.98 руб. | Оплачен

Иван@store $ review a1b2c3d4 5 Отличная футболка

Отзыв добавлен! Оценка: 5/5

Иван@store $ exit

До свидания! Спасибо за покупки!

## Тестирование

**Файл:** `tests.py`

### Структура тестов

- `TestProduct` — 4 теста для класса Product
- `TestUser` — 3 теста для класса User
- `TestCart` — 9 тестов для класса Cart
- `TestOrder` — 7 тестов для класса Order
- `TestPayment` — 3 теста для класса Payment
- `TestDelivery` — 4 теста для класса Delivery
- `TestReview` — 2 теста для класса Review
- `TestPromoCode` — 3 теста для класса PromoCode
- `TestStoreService` — 23 теста для сервисов

Итого: 58 unit-тестов

## Принципы ООП

**Инкапсуляция**
Приватные атрибуты в классах models.py обозначены как внутренние. Доступ к данным осуществляется через публичные методы.

**Наследование**
Классы User, Seller, Product, Order, Payment, Delivery, Review, PromoCode наследуются от базового класса Entity. Все исключения наследуются от StoreException.

**Полиморфизм**
Разные классы исключений реализуют свои конструкторы с разными параметрами, наследуя общее поведение от базового класса.

**Абстракция**
Выделены ключевые сущности предметной области: User, Product, Cart, Order, Payment, Delivery, Review, PromoCode. Каждая сущность имеет чёткие границы ответственности.

**Принцип единственной ответственности**
Каждый класс отвечает за одну функцию:
- User — хранение данных пользователя
- Product — хранение данных товара
- Cart — управление корзиной
- Order — хранение данных заказа
- Payment — управление оплатой
- Delivery — управление доставкой
- Review — хранение отзывов
- PromoCode — управление промокодами
- StoreService — бизнес-логика

## Установка и запуск

```bash
# Клонирование репозитория
git clone https://github.com/ваш-репозиторий/clothing_store.git

# Запуск программы
python main.py

# Запуск тестов
python -m unittest tests.py -v
```

## Требования
Python 3.10 или выше

Внешние библиотеки не требуются