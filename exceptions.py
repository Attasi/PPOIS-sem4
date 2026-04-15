"""
Модуль с пользовательскими исключениями для интернет-магазина одежды.
"""


class StoreException(Exception):
    def __init__(self, message: str = "Произошла ошибка в магазине"):
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}: {self.message}"


class AuthenticationError(StoreException):
    def __init__(self, message: str = "Ошибка аутентификации"):
        super().__init__(message)


class UserAlreadyExistsError(AuthenticationError):
    def __init__(self, email: str):
        message = f"Пользователь с email '{email}' уже существует"
        super().__init__(message)


class UserNotFoundError(AuthenticationError):
    def __init__(self, email: str):
        message = f"Пользователь с email '{email}' не найден"
        super().__init__(message)


class InvalidPasswordError(AuthenticationError):
    def __init__(self):
        message = "Неверный пароль"
        super().__init__(message)


class NotAuthenticatedError(AuthenticationError):
    def __init__(self):
        message = "Необходимо войти в систему"
        super().__init__(message)


class ProductError(StoreException):
    def __init__(self, message: str = "Ошибка при работе с товаром"):
        super().__init__(message)


class ProductNotFoundError(ProductError):
    def __init__(self, product_id: str):
        message = f"Товар с ID '{product_id}' не найден"
        super().__init__(message)


class InsufficientStockError(ProductError):
    def __init__(self, product_name: str, available: int, requested: int):
        message = f"Недостаточно товара '{product_name}'. Доступно: {available}, запрошено: {requested}"
        super().__init__(message)


class ProductNotAvailableError(ProductError):
    def __init__(self, product_name: str):
        message = f"Товар '{product_name}' временно недоступен"
        super().__init__(message)


class CartError(StoreException):
    def __init__(self, message: str = "Ошибка при работе с корзиной"):
        super().__init__(message)


class CartEmptyError(CartError):
    def __init__(self):
        message = "Корзина пуста. Добавьте товары перед оформлением заказа"
        super().__init__(message)


class CartItemNotFoundError(CartError):
    def __init__(self, product_id: str):
        message = f"Товар с ID '{product_id}' не найден в корзине"
        super().__init__(message)


class OrderError(StoreException):
    def __init__(self, message: str = "Ошибка при работе с заказом"):
        super().__init__(message)


class OrderNotFoundError(OrderError):
    def __init__(self, order_id: str):
        message = f"Заказ с ID '{order_id}' не найден"
        super().__init__(message)


class OrderNotBelongToUserError(OrderError):
    def __init__(self, order_id: str, user_id: str):
        message = f"Заказ '{order_id}' не принадлежит пользователю '{user_id}'"
        super().__init__(message)


class InvalidOrderStatusError(OrderError):
    def __init__(self, order_id: str, current_status: str, action: str):
        message = f"Невозможно выполнить '{action}' для заказа '{order_id}' в статусе '{current_status}'"
        super().__init__(message)


class OrderCannotBePaidError(InvalidOrderStatusError):
    def __init__(self, order_id: str, current_status: str):
        super().__init__(order_id, current_status, "оплату")


class OrderCannotBeCancelledError(InvalidOrderStatusError):
    def __init__(self, order_id: str, current_status: str):
        super().__init__(order_id, current_status, "отмену")


class OrderCannotBeReturnedError(InvalidOrderStatusError):
    def __init__(self, order_id: str, current_status: str):
        super().__init__(order_id, current_status, "возврат")


class PaymentError(StoreException):
    def __init__(self, message: str = "Ошибка при оплате"):
        super().__init__(message)


class PaymentNotFoundError(PaymentError):
    def __init__(self, order_id: str):
        message = f"Платёж для заказа '{order_id}' не найден"
        super().__init__(message)


class PaymentAlreadyProcessedError(PaymentError):
    def __init__(self, payment_id: str):
        message = f"Платёж '{payment_id}' уже был обработан"
        super().__init__(message)


class PaymentFailedError(PaymentError):
    def __init__(self, reason: str = "Неизвестная ошибка"):
        message = f"Ошибка при оплате: {reason}"
        super().__init__(message)


class DeliveryError(StoreException):
    def __init__(self, message: str = "Ошибка при доставке"):
        super().__init__(message)


class DeliveryNotFoundError(DeliveryError):
    def __init__(self, order_id: str):
        message = f"Информация о доставке для заказа '{order_id}' не найдена"
        super().__init__(message)


class DeliveryAlreadyStartedError(DeliveryError):
    def __init__(self, delivery_id: str):
        message = f"Доставка '{delivery_id}' уже начата"
        super().__init__(message)


class TrackingNumberRequiredError(DeliveryError):
    def __init__(self):
        message = "Для начала доставки необходимо указать трек-номер"
        super().__init__(message)


class InvalidDeliveryStatusError(DeliveryError):
    def __init__(self, current_status: str, target_status: str):
        message = f"Невозможно изменить статус с '{current_status}' на '{target_status}'"
        super().__init__(message)


class PromoCodeError(StoreException):
    def __init__(self, message: str = "Ошибка при работе с промокодом"):
        super().__init__(message)


class PromoCodeNotFoundError(PromoCodeError):
    def __init__(self, code: str):
        message = f"Промокод '{code}' не найден"
        super().__init__(message)


class PromoCodeExpiredError(PromoCodeError):
    def __init__(self, code: str, expires_at: str):
        message = f"Промокод '{code}' истёк {expires_at}"
        super().__init__(message)


class PromoCodeAlreadyUsedError(PromoCodeError):
    def __init__(self, code: str):
        message = f"Промокод '{code}' уже был использован"
        super().__init__(message)


class ReviewError(StoreException):
    def __init__(self, message: str = "Ошибка при работе с отзывом"):
        super().__init__(message)


class InvalidRatingError(ReviewError):
    def __init__(self, rating: int):
        message = f"Некорректная оценка: {rating}. Оценка должна быть от 1 до 5"
        super().__init__(message)


class InvalidOperationError(StoreException):
    def __init__(self, message: str = "Некорректная операция"):
        super().__init__(message)


class ValidationError(StoreException):
    def __init__(self, field: str, message: str):
        super().__init__(f"Ошибка валидации поля '{field}': {message}")