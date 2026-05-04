from datetime import datetime
from typing import List, Optional

from models import (
    User, Seller, Product, Cart, Order, Payment, Delivery,
    ProductCategory, OrderStatus, PaymentStatus, DeliveryStatus,
    CartItem, Review, PromoCode
)

from exceptions import (
    InvalidOperationError,
    ValidationError,
    UserAlreadyExistsError,
    UserNotFoundError,
    InvalidPasswordError,
    NotAuthenticatedError,
    ProductNotFoundError,
    InsufficientStockError,
    ProductNotAvailableError,
    CartEmptyError,
    OrderNotFoundError,
    OrderNotBelongToUserError,
    OrderCannotBePaidError,
    OrderCannotBeReturnedError,
    PaymentNotFoundError,
    PaymentFailedError,
    DeliveryNotFoundError,
    TrackingNumberRequiredError,
    PromoCodeNotFoundError,
    InvalidRatingError
)


class StoreService:

    def __init__(self):
        self.users: List[User] = []
        self.sellers: List[Seller] = []
        self.products: List[Product] = []
        self.carts: List[Cart] = []
        self.orders: List[Order] = []
        self.reviews: List[Review] = []
        self.promocodes: List[PromoCode] = []
        self.current_user: Optional[User] = None

    def _check_authenticated(self) -> None:
        if not self.current_user:
            raise NotAuthenticatedError()

    def register(self, email: str, name: str, password: str) -> User:
        if not email or "@" not in email:
            raise ValidationError("email", "Некорректный email адрес")
        if not password or len(password) < 3:
            raise ValidationError("password", "Пароль должен содержать минимум 3 символа")

        for user in self.users:
            if user.email == email:
                raise UserAlreadyExistsError(email)

        user = User(email=email, name=name, password_hash=password)
        self.users.append(user)
        self.carts.append(Cart(user_id=user.id))
        return user

    def login(self, email: str, password: str) -> User:
        user = None
        for u in self.users:
            if u.email == email:
                user = u
                break

        if not user:
            raise UserNotFoundError(email)
        if not user.verify_password(password):
            raise InvalidPasswordError()

        self.current_user = user
        return user

    def logout(self) -> None:
        self.current_user = None

    def search_products(self, query: str = "", category: Optional[ProductCategory] = None,
                        min_price: Optional[float] = None, max_price: Optional[float] = None) -> List[Product]:
        results = self.products.copy()

        if query:
            query_lower = query.lower()
            results = [p for p in results if query_lower in p.name.lower() or query_lower in p.description.lower()]
        if category:
            results = [p for p in results if p.category == category]
        if min_price is not None:
            results = [p for p in results if p.price >= min_price]
        if max_price is not None:
            results = [p for p in results if p.price <= max_price]

        return results

    def _get_current_cart(self) -> Cart:
        self._check_authenticated()
        for cart in self.carts:
            if cart.user_id == self.current_user.id:
                return cart
        cart = Cart(user_id=self.current_user.id)
        self.carts.append(cart)
        return cart

    def add_to_cart(self, product_id: str, quantity: int = 1) -> None:
        self._check_authenticated()
        if quantity <= 0:
            raise ValidationError("quantity", "Количество должно быть положительным числом")

        product = self.get_product_by_id(product_id)
        if not product:
            raise ProductNotFoundError(product_id)
        if product.stock <= 0:
            raise ProductNotAvailableError(product.name)

        cart = self._get_current_cart()
        cart.add_product(product, quantity)

    def remove_from_cart(self, product_id: str) -> None:
        self._check_authenticated()
        cart = self._get_current_cart()
        cart.remove_product(product_id)

    def update_cart_quantity(self, product_id: str, quantity: int) -> None:
        self._check_authenticated()
        cart = self._get_current_cart()
        cart.update_quantity(product_id, quantity)

    def view_cart(self) -> Cart:
        return self._get_current_cart()

    def create_order(self, address: str, promo_code: Optional[str] = None) -> Order:
        self._check_authenticated()
        cart = self._get_current_cart()

        if not cart.items:
            raise CartEmptyError()

        for item in cart.items:
            if item.quantity > item.product.stock:
                raise InsufficientStockError(item.product.name, item.product.stock, item.quantity)

        total = cart.get_total()

        if promo_code:
            found_promo = None
            for pc in self.promocodes:
                if pc.code == promo_code:
                    found_promo = pc
                    break
            if not found_promo:
                raise PromoCodeNotFoundError(promo_code)
            total = found_promo.apply(total)

        order_items = [CartItem(product=item.product, quantity=item.quantity) for item in cart.items]

        order = Order(user_id=self.current_user.id, items=order_items, total_amount=total)
        order.payment = Payment(order_id=order.id, amount=total)
        order.delivery = Delivery(order_id=order.id, address=address)

        self.orders.append(order)

        for item in cart.items:
            item.product.reduce_stock(item.quantity)

        cart.clear()
        return order

    def pay_order(self, order_id: str) -> None:
        self._check_authenticated()

        order = self.get_order_by_id(order_id)
        if not order:
            raise OrderNotFoundError(order_id)
        if order.user_id != self.current_user.id:
            raise OrderNotBelongToUserError(order_id, self.current_user.id)
        if not order.can_pay():
            raise OrderCannotBePaidError(order_id, order.status.value)
        if not order.payment:
            raise PaymentNotFoundError(order_id)

        try:
            order.payment.complete()
            order.status = OrderStatus.PAID
        except Exception as e:
            order.payment.status = PaymentStatus.FAILED
            raise PaymentFailedError(str(e))

    def track_delivery(self, order_id: str) -> Delivery:
        self._check_authenticated()

        order = self.get_order_by_id(order_id)
        if not order:
            raise OrderNotFoundError(order_id)
        if order.user_id != self.current_user.id:
            raise OrderNotBelongToUserError(order_id, self.current_user.id)
        if not order.delivery:
            raise DeliveryNotFoundError(order_id)

        return order.delivery

    def update_delivery_status(self, order_id: str, new_status: DeliveryStatus,
                               tracking_number: Optional[str] = None) -> None:
        order = self.get_order_by_id(order_id)
        if not order:
            raise OrderNotFoundError(order_id)
        if not order.delivery:
            raise DeliveryNotFoundError(order_id)

        delivery = order.delivery

        if new_status == DeliveryStatus.IN_TRANSIT:
            if not tracking_number:
                raise TrackingNumberRequiredError()
            delivery.start_delivery(tracking_number)
        elif new_status == DeliveryStatus.DELIVERED:
            delivery.mark_delivered()
            order.status = OrderStatus.DELIVERED
        else:
            delivery.status = new_status

    def request_return(self, order_id: str) -> Order:
        self._check_authenticated()

        order = self.get_order_by_id(order_id)
        if not order:
            raise OrderNotFoundError(order_id)
        if order.user_id != self.current_user.id:
            raise OrderNotBelongToUserError(order_id, self.current_user.id)
        if not order.can_return():
            raise OrderCannotBeReturnedError(order_id, order.status.value)

        order.status = OrderStatus.RETURNED
        for item in order.items:
            item.product.increase_stock(item.quantity)

        if order.payment and order.payment.status == PaymentStatus.COMPLETED:
            order.payment.status = PaymentStatus.REFUNDED

        return order

    def add_review(self, product_id: str, rating: int, comment: str) -> Review:
        self._check_authenticated()

        if rating < 1 or rating > 5:
            raise InvalidRatingError(rating)

        product = self.get_product_by_id(product_id)
        if not product:
            raise ProductNotFoundError(product_id)

        review = Review(product_id=product_id, user_id=self.current_user.id, rating=rating, comment=comment)
        self.reviews.append(review)
        return review

    def add_product(self, name: str, description: str, price: float,
                    category: ProductCategory, seller_id: str, stock: int) -> Product:
        if price <= 0:
            raise ValidationError("price", "Цена должна быть положительным числом")
        if stock < 0:
            raise ValidationError("stock", "Количество не может быть отрицательным")
        if not name or not name.strip():
            raise ValidationError("name", "Название товара не может быть пустым")

        product = Product(name=name, description=description, price=price,
                          category=category, seller_id=seller_id, stock=stock)
        self.products.append(product)
        return product

    def add_seller(self, name: str, contact_email: str) -> Seller:
        if not contact_email or "@" not in contact_email:
            raise ValidationError("contact_email", "Некорректный email адрес")

        seller = Seller(name=name, contact_email=contact_email)
        self.sellers.append(seller)
        return seller

    def add_promo_code(self, code: str, discount_percent: float, expires_at: datetime) -> PromoCode:
        if discount_percent <= 0 or discount_percent > 100:
            raise ValidationError("discount_percent", "Процент скидки должен быть от 1 до 100")

        promo = PromoCode(code=code, discount_percent=discount_percent, expires_at=expires_at)
        self.promocodes.append(promo)
        return promo

    def get_user_orders(self) -> List[Order]:
        self._check_authenticated()
        return [order for order in self.orders if order.user_id == self.current_user.id]

    def get_order_by_id(self, order_id: str) -> Optional[Order]:
        for order in self.orders:
            if order.id == order_id:
                return order
        return None

    def get_product_by_id(self, product_id: str) -> Optional[Product]:
        for product in self.products:
            if product.id == product_id or product.id.startswith(product_id):
                return product
        return None