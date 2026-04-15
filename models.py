from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import uuid4

from exceptions import (
    InsufficientStockError,
    PaymentAlreadyProcessedError,
    DeliveryAlreadyStartedError,
    InvalidDeliveryStatusError,
    PromoCodeExpiredError,
    PromoCodeAlreadyUsedError,
    InvalidRatingError
)


class ProductCategory(Enum):
    MEN = "Мужская одежда"
    WOMEN = "Женская одежда"
    KIDS = "Детская одежда"
    ACCESSORIES = "Аксессуары"


class OrderStatus(Enum):
    PENDING = "Ожидает оплаты"
    PAID = "Оплачен"
    PROCESSING = "В обработке"
    SHIPPED = "Отправлен"
    DELIVERED = "Доставлен"
    CANCELLED = "Отменён"
    RETURNED = "Возвращён"


class DeliveryStatus(Enum):
    AWAITING_PICKUP = "Ожидает передачи в доставку"
    IN_TRANSIT = "В пути"
    DELIVERED = "Доставлен"


class PaymentStatus(Enum):
    PENDING = "Ожидает оплаты"
    COMPLETED = "Оплачено"
    FAILED = "Ошибка оплаты"
    REFUNDED = "Возвращено"


@dataclass(kw_only=True)
class Entity:
    id: str = field(default_factory=lambda: str(uuid4()))

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id})"


@dataclass(kw_only=True)
class User(Entity):
    email: str
    name: str
    password_hash: str
    registered_at: datetime = field(default_factory=datetime.now)

    def verify_password(self, plain_password: str) -> bool:
        return self.password_hash == plain_password


@dataclass(kw_only=True)
class Seller(Entity):
    name: str
    contact_email: str


@dataclass(kw_only=True)
class Product(Entity):
    name: str
    description: str
    price: float
    category: ProductCategory
    seller_id: str
    stock: int
    created_at: datetime = field(default_factory=datetime.now)

    def reduce_stock(self, quantity: int) -> None:
        if quantity > self.stock:
            raise InsufficientStockError(self.name, self.stock, quantity)
        self.stock -= quantity

    def increase_stock(self, quantity: int) -> None:
        self.stock += quantity


@dataclass
class CartItem:
    product: Product
    quantity: int


@dataclass
class Cart:
    user_id: str
    items: List[CartItem] = field(default_factory=list)

    def add_product(self, product: Product, quantity: int = 1) -> None:
        for item in self.items:
            if item.product.id == product.id:
                item.quantity += quantity
                return
        self.items.append(CartItem(product, quantity))

    def remove_product(self, product_id: str) -> None:
        self.items = [item for item in self.items if item.product.id != product_id]

    def update_quantity(self, product_id: str, quantity: int) -> None:
        for item in self.items:
            if item.product.id == product_id:
                if quantity <= 0:
                    self.remove_product(product_id)
                else:
                    item.quantity = quantity
                return

    def clear(self) -> None:
        self.items.clear()

    def get_total(self) -> float:
        return sum(item.product.price * item.quantity for item in self.items)

    def get_items_count(self) -> int:
        return sum(item.quantity for item in self.items)


@dataclass(kw_only=True)
class Order(Entity):
    user_id: str
    items: List[CartItem]
    total_amount: float
    status: OrderStatus = OrderStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    payment: Optional['Payment'] = None
    delivery: Optional['Delivery'] = None

    def can_pay(self) -> bool:
        return self.status == OrderStatus.PENDING

    def can_cancel(self) -> bool:
        return self.status in (OrderStatus.PENDING, OrderStatus.PAID, OrderStatus.PROCESSING)

    def can_return(self) -> bool:
        return self.status == OrderStatus.DELIVERED


@dataclass(kw_only=True)
class Payment(Entity):
    order_id: str
    amount: float
    status: PaymentStatus = PaymentStatus.PENDING
    paid_at: Optional[datetime] = None

    def complete(self) -> None:
        if self.status != PaymentStatus.PENDING:
            raise PaymentAlreadyProcessedError(self.id)
        self.status = PaymentStatus.COMPLETED
        self.paid_at = datetime.now()


@dataclass(kw_only=True)
class Delivery(Entity):
    order_id: str
    address: str
    status: DeliveryStatus = DeliveryStatus.AWAITING_PICKUP
    tracking_number: Optional[str] = None
    shipped_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None

    def start_delivery(self, tracking_number: str) -> None:
        if self.status != DeliveryStatus.AWAITING_PICKUP:
            raise DeliveryAlreadyStartedError(self.id)
        self.tracking_number = tracking_number
        self.status = DeliveryStatus.IN_TRANSIT
        self.shipped_at = datetime.now()

    def mark_delivered(self) -> None:
        if self.status != DeliveryStatus.IN_TRANSIT:
            raise InvalidDeliveryStatusError(self.status.value, DeliveryStatus.DELIVERED.value)
        self.status = DeliveryStatus.DELIVERED
        self.delivered_at = datetime.now()


@dataclass(kw_only=True)
class Review(Entity):
    product_id: str
    user_id: str
    rating: int
    comment: str
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        if self.rating < 1 or self.rating > 5:
            raise InvalidRatingError(self.rating)


@dataclass(kw_only=True)
class PromoCode(Entity):
    code: str
    discount_percent: float
    expires_at: datetime
    used: bool = False

    def apply(self, amount: float) -> float:
        if self.used:
            raise PromoCodeAlreadyUsedError(self.code)
        if datetime.now() > self.expires_at:
            raise PromoCodeExpiredError(self.code, self.expires_at.strftime("%Y-%m-%d %H:%M:%S"))
        discount = amount * (self.discount_percent / 100)
        return amount - discount