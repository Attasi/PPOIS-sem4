import unittest
from datetime import datetime, timedelta

from models import (
    Product, ProductCategory, User, Cart, CartItem,
    Order, Payment, Delivery, Review, PromoCode,
    OrderStatus, PaymentStatus, DeliveryStatus
)

from services import StoreService

from exceptions import (
    ProductNotFoundError,
    InsufficientStockError,
    CartEmptyError,
    OrderNotFoundError,
    OrderCannotBePaidError,
    OrderCannotBeReturnedError,
    UserAlreadyExistsError,
    InvalidPasswordError,
    NotAuthenticatedError,
    InvalidRatingError,
    PromoCodeNotFoundError,
    PromoCodeExpiredError,
    PromoCodeAlreadyUsedError
)


class TestProduct(unittest.TestCase):
    def setUp(self):
        self.product = Product(
            name="Футболка",
            description="Хлопковая футболка",
            price=1000.0,
            category=ProductCategory.MEN,
            seller_id="seller1",
            stock=10
        )

    def test_product_creation(self):
        self.assertEqual(self.product.name, "Футболка")
        self.assertEqual(self.product.price, 1000.0)
        self.assertEqual(self.product.stock, 10)
        self.assertIsNotNone(self.product.id)

    def test_reduce_stock_success(self):
        self.product.reduce_stock(3)
        self.assertEqual(self.product.stock, 7)

    def test_reduce_stock_insufficient(self):
        with self.assertRaises(InsufficientStockError):
            self.product.reduce_stock(15)

    def test_increase_stock(self):
        self.product.increase_stock(5)
        self.assertEqual(self.product.stock, 15)


class TestUser(unittest.TestCase):
    def setUp(self):
        self.user = User(
            email="test@test.com",
            name="Тестовый Пользователь",
            password_hash="password123"
        )

    def test_user_creation(self):
        self.assertEqual(self.user.email, "test@test.com")
        self.assertEqual(self.user.name, "Тестовый Пользователь")
        self.assertIsNotNone(self.user.id)
        self.assertIsNotNone(self.user.registered_at)

    def test_verify_password_correct(self):
        self.assertTrue(self.user.verify_password("password123"))

    def test_verify_password_incorrect(self):
        self.assertFalse(self.user.verify_password("wrongpass"))


class TestCart(unittest.TestCase):
    def setUp(self):
        self.product = Product(
            name="Футболка",
            description="Хлопковая футболка",
            price=1000.0,
            category=ProductCategory.MEN,
            seller_id="seller1",
            stock=10
        )
        self.cart = Cart(user_id="user1")

    def test_add_product_new(self):
        self.cart.add_product(self.product, 2)
        self.assertEqual(len(self.cart.items), 1)
        self.assertEqual(self.cart.items[0].quantity, 2)

    def test_add_product_existing(self):
        self.cart.add_product(self.product, 2)
        self.cart.add_product(self.product, 3)
        self.assertEqual(len(self.cart.items), 1)
        self.assertEqual(self.cart.items[0].quantity, 5)

    def test_remove_product(self):
        self.cart.add_product(self.product, 2)
        self.cart.remove_product(self.product.id)
        self.assertEqual(len(self.cart.items), 0)

    def test_update_quantity(self):
        self.cart.add_product(self.product, 2)
        self.cart.update_quantity(self.product.id, 5)
        self.assertEqual(self.cart.items[0].quantity, 5)

    def test_update_quantity_zero(self):
        self.cart.add_product(self.product, 2)
        self.cart.update_quantity(self.product.id, 0)
        self.assertEqual(len(self.cart.items), 0)

    def test_get_total(self):
        self.cart.add_product(self.product, 2)
        self.assertEqual(self.cart.get_total(), 2000.0)

    def test_get_items_count(self):
        self.cart.add_product(self.product, 2)
        self.assertEqual(self.cart.get_items_count(), 2)

    def test_clear(self):
        self.cart.add_product(self.product, 2)
        self.cart.clear()
        self.assertEqual(len(self.cart.items), 0)


class TestOrder(unittest.TestCase):
    def setUp(self):
        self.product = Product(
            name="Футболка",
            description="Хлопковая футболка",
            price=1000.0,
            category=ProductCategory.MEN,
            seller_id="seller1",
            stock=10
        )
        self.order = Order(
            user_id="user1",
            items=[CartItem(product=self.product, quantity=2)],
            total_amount=2000.0
        )

    def test_order_creation(self):
        self.assertEqual(self.order.user_id, "user1")
        self.assertEqual(self.order.total_amount, 2000.0)
        self.assertEqual(self.order.status, OrderStatus.PENDING)

    def test_can_pay_pending(self):
        self.assertTrue(self.order.can_pay())

    def test_can_pay_paid(self):
        self.order.status = OrderStatus.PAID
        self.assertFalse(self.order.can_pay())

    def test_can_cancel_pending(self):
        self.assertTrue(self.order.can_cancel())

    def test_can_cancel_delivered(self):
        self.order.status = OrderStatus.DELIVERED
        self.assertFalse(self.order.can_cancel())

    def test_can_return_delivered(self):
        self.order.status = OrderStatus.DELIVERED
        self.assertTrue(self.order.can_return())

    def test_can_return_pending(self):
        self.assertFalse(self.order.can_return())


class TestPayment(unittest.TestCase):
    def setUp(self):
        self.payment = Payment(order_id="order1", amount=1000.0)

    def test_payment_creation(self):
        self.assertEqual(self.payment.order_id, "order1")
        self.assertEqual(self.payment.amount, 1000.0)
        self.assertEqual(self.payment.status, PaymentStatus.PENDING)

    def test_complete_success(self):
        self.payment.complete()
        self.assertEqual(self.payment.status, PaymentStatus.COMPLETED)
        self.assertIsNotNone(self.payment.paid_at)

    def test_complete_already_processed(self):
        self.payment.complete()
        with self.assertRaises(Exception):
            self.payment.complete()


class TestDelivery(unittest.TestCase):
    def setUp(self):
        self.delivery = Delivery(order_id="order1", address="г. Москва")

    def test_delivery_creation(self):
        self.assertEqual(self.delivery.order_id, "order1")
        self.assertEqual(self.delivery.address, "г. Москва")
        self.assertEqual(self.delivery.status, DeliveryStatus.AWAITING_PICKUP)

    def test_start_delivery_success(self):
        self.delivery.start_delivery("TRACK123")
        self.assertEqual(self.delivery.status, DeliveryStatus.IN_TRANSIT)
        self.assertEqual(self.delivery.tracking_number, "TRACK123")
        self.assertIsNotNone(self.delivery.shipped_at)

    def test_start_delivery_already_started(self):
        self.delivery.start_delivery("TRACK123")
        with self.assertRaises(Exception):
            self.delivery.start_delivery("TRACK456")

    def test_mark_delivered_success(self):
        self.delivery.start_delivery("TRACK123")
        self.delivery.mark_delivered()
        self.assertEqual(self.delivery.status, DeliveryStatus.DELIVERED)
        self.assertIsNotNone(self.delivery.delivered_at)


class TestReview(unittest.TestCase):
    def test_review_creation_valid_rating(self):
        review = Review(
            product_id="product1",
            user_id="user1",
            rating=5,
            comment="Отличный товар!"
        )
        self.assertEqual(review.rating, 5)

    def test_review_invalid_rating(self):
        with self.assertRaises(InvalidRatingError):
            Review(
                product_id="product1",
                user_id="user1",
                rating=6,
                comment="Слишком высокая оценка"
            )


class TestPromoCode(unittest.TestCase):
    def setUp(self):
        self.promo = PromoCode(
            code="TEST10",
            discount_percent=10,
            expires_at=datetime.now() + timedelta(days=30)
        )

    def test_apply_success(self):
        result = self.promo.apply(1000.0)
        self.assertEqual(result, 900.0)

    def test_apply_already_used(self):
        self.promo.used = True
        with self.assertRaises(PromoCodeAlreadyUsedError):
            self.promo.apply(1000.0)

    def test_apply_expired(self):
        self.promo.expires_at = datetime.now() - timedelta(days=1)
        with self.assertRaises(PromoCodeExpiredError):
            self.promo.apply(1000.0)


class TestStoreService(unittest.TestCase):
    def setUp(self):
        self.service = StoreService()
        self.seller = self.service.add_seller("Тестовый Продавец", "seller@test.com")

        self.product1 = self.service.add_product(
            name="Футболка",
            description="Хлопковая футболка",
            price=1000.0,
            category=ProductCategory.MEN,
            seller_id=self.seller.id,
            stock=10
        )

        self.product2 = self.service.add_product(
            name="Джинсы",
            description="Синие джинсы",
            price=2500.0,
            category=ProductCategory.MEN,
            seller_id=self.seller.id,
            stock=5
        )

        self.user = self.service.register("user@test.com", "Тестовый Пользователь", "password123")
        self.service.login("user@test.com", "password123")

    def test_register_success(self):
        user = self.service.register("new@test.com", "Новый Пользователь", "pass123")
        self.assertEqual(user.email, "new@test.com")
        self.assertEqual(len(self.service.users), 2)

    def test_register_duplicate_email(self):
        with self.assertRaises(UserAlreadyExistsError):
            self.service.register("user@test.com", "Другой", "pass123")

    def test_login_success(self):
        self.service.logout()
        user = self.service.login("user@test.com", "password123")
        self.assertEqual(user.email, "user@test.com")

    def test_login_invalid_password(self):
        self.service.logout()
        with self.assertRaises(InvalidPasswordError):
            self.service.login("user@test.com", "wrongpass")

    def test_search_products_by_name(self):
        results = self.service.search_products("футболка")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "Футболка")

    def test_search_products_by_category(self):
        results = self.service.search_products(category=ProductCategory.MEN)
        self.assertEqual(len(results), 2)

    def test_add_to_cart_success(self):
        self.service.add_to_cart(self.product1.id, 2)
        cart = self.service.view_cart()
        self.assertEqual(cart.get_items_count(), 2)
        self.assertEqual(cart.get_total(), 2000.0)

    def test_add_to_cart_product_not_found(self):
        with self.assertRaises(ProductNotFoundError):
            self.service.add_to_cart("non-existent-id", 1)

    def test_add_to_cart_not_authenticated(self):
        self.service.logout()
        with self.assertRaises(NotAuthenticatedError):
            self.service.add_to_cart(self.product1.id, 1)

    def test_create_order_success(self):
        self.service.add_to_cart(self.product1.id, 2)
        order = self.service.create_order("г. Москва, ул. Ленина 1")
        self.assertEqual(order.total_amount, 2000.0)
        self.assertEqual(order.status, OrderStatus.PENDING)
        self.assertEqual(len(order.items), 1)
        self.assertEqual(order.items[0].quantity, 2)

    def test_create_order_empty_cart(self):
        with self.assertRaises(CartEmptyError):
            self.service.create_order("г. Москва")

    def test_create_order_insufficient_stock(self):
        self.service.add_to_cart(self.product1.id, 15)
        with self.assertRaises(InsufficientStockError):
            self.service.create_order("г. Москва")

    def test_pay_order_success(self):
        self.service.add_to_cart(self.product1.id, 1)
        order = self.service.create_order("г. Москва")
        self.service.pay_order(order.id)
        self.assertEqual(order.status, OrderStatus.PAID)
        self.assertEqual(order.payment.status, PaymentStatus.COMPLETED)

    def test_pay_order_not_found(self):
        with self.assertRaises(OrderNotFoundError):
            self.service.pay_order("non-existent-id")

    def test_pay_order_already_paid(self):
        self.service.add_to_cart(self.product1.id, 1)
        order = self.service.create_order("г. Москва")
        self.service.pay_order(order.id)
        with self.assertRaises(OrderCannotBePaidError):
            self.service.pay_order(order.id)

    def test_track_delivery(self):
        self.service.add_to_cart(self.product1.id, 1)
        order = self.service.create_order("г. Москва")
        delivery = self.service.track_delivery(order.id)
        self.assertEqual(delivery.order_id, order.id)
        self.assertEqual(delivery.status, DeliveryStatus.AWAITING_PICKUP)

    def test_return_order_success(self):
        self.service.add_to_cart(self.product1.id, 1)
        order = self.service.create_order("г. Москва")
        self.service.pay_order(order.id)
        self.service.update_delivery_status(order.id, DeliveryStatus.IN_TRANSIT, "TRACK123")
        self.service.update_delivery_status(order.id, DeliveryStatus.DELIVERED)
        returned = self.service.request_return(order.id)
        self.assertEqual(returned.status, OrderStatus.RETURNED)
        self.assertEqual(returned.payment.status, PaymentStatus.REFUNDED)

    def test_return_order_not_delivered(self):
        self.service.add_to_cart(self.product1.id, 1)
        order = self.service.create_order("г. Москва")
        with self.assertRaises(OrderCannotBeReturnedError):
            self.service.request_return(order.id)

    def test_add_review_success(self):
        review = self.service.add_review(self.product1.id, 5, "Отличный товар!")
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.comment, "Отличный товар!")

    def test_add_review_invalid_rating(self):
        with self.assertRaises(InvalidRatingError):
            self.service.add_review(self.product1.id, 6, "Слишком высокая оценка")

    def test_add_review_product_not_found(self):
        with self.assertRaises(ProductNotFoundError):
            self.service.add_review("non-existent-id", 5, "Отзыв")

    def test_apply_promo_code(self):
        self.service.add_promo_code("TEST10", 10.0, datetime.now() + timedelta(days=30))
        self.service.add_to_cart(self.product1.id, 1)
        order = self.service.create_order("г. Москва", "TEST10")
        self.assertEqual(order.total_amount, 900.0)

    def test_promo_code_not_found(self):
        self.service.add_to_cart(self.product1.id, 1)
        with self.assertRaises(PromoCodeNotFoundError):
            self.service.create_order("г. Москва", "NONEXISTENT")

    def test_get_user_orders(self):
        self.service.add_to_cart(self.product1.id, 1)
        order1 = self.service.create_order("Адрес 1")
        self.service.add_to_cart(self.product2.id, 1)
        order2 = self.service.create_order("Адрес 2")
        orders = self.service.get_user_orders()
        self.assertEqual(len(orders), 2)
        self.assertTrue(any(o.id == order1.id for o in orders))
        self.assertTrue(any(o.id == order2.id for o in orders))


if __name__ == "__main__":
    unittest.main(verbosity=2)