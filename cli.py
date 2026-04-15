import sys
from typing import Dict, Callable
from datetime import datetime, timedelta

from services import StoreService
from models import ProductCategory
from exceptions import (
    StoreException,
    NotAuthenticatedError,
    ProductNotFoundError,
    InsufficientStockError,
    CartEmptyError,
    OrderNotFoundError,
    OrderCannotBePaidError,
    OrderCannotBeReturnedError,
    ValidationError,
    InvalidRatingError
)


class ClothingStoreCLI:

    def __init__(self):
        self.service = StoreService()
        self._setup_test_data()
        self._init_commands()

    def _setup_test_data(self) -> None:
        seller = self.service.add_seller("Модный Дом", "contact@modny-dom.ru")

        self.service.add_product(
            name="Футболка хлопковая белая",
            description="Классическая белая футболка из 100% хлопка",
            price=1299.99,
            category=ProductCategory.MEN,
            seller_id=seller.id,
            stock=25
        )

        self.service.add_product(
            name="Джинсы скинни синие",
            description="Узкие джинсы с высокой посадкой",
            price=3499.99,
            category=ProductCategory.MEN,
            seller_id=seller.id,
            stock=15
        )

        self.service.add_product(
            name="Платье летнее цветочное",
            description="Легкое платье с цветочным принтом",
            price=2799.99,
            category=ProductCategory.WOMEN,
            seller_id=seller.id,
            stock=10
        )

        self.service.add_product(
            name="Сумка кожаная черная",
            description="Стильная сумка из натуральной кожи",
            price=4599.99,
            category=ProductCategory.ACCESSORIES,
            seller_id=seller.id,
            stock=8
        )

        self.service.add_product(
            name="Детская футболка с принтом",
            description="Футболка с ярким принтом для детей",
            price=899.99,
            category=ProductCategory.KIDS,
            seller_id=seller.id,
            stock=20
        )

        self.service.add_promo_code(
            code="WELCOME10",
            discount_percent=10,
            expires_at=datetime.now() + timedelta(days=30)
        )

        self.service.add_promo_code(
            code="SALE20",
            discount_percent=20,
            expires_at=datetime.now() + timedelta(days=7)
        )

    def _init_commands(self) -> None:
        self.commands: Dict[str, Callable] = {
            "help": self._show_help,
            "exit": self._exit,
            "quit": self._exit,
            "register": self._register,
            "login": self._login,
            "logout": self._logout,
            "whoami": self._whoami,
            "list": self._list_products,
            "search": self._search_products,
            "info": self._product_info,
            "cart": self._show_cart,
            "add": self._add_to_cart,
            "remove": self._remove_from_cart,
            "update": self._update_cart,
            "clear": self._clear_cart,
            "checkout": self._checkout,
            "pay": self._pay_order,
            "orders": self._show_orders,
            "order": self._order_details,
            "track": self._track_delivery,
            "return": self._return_order,
            "review": self._add_review,
            "add_product": self._add_product_admin,
            "add_promo": self._add_promo_admin,
        }

    def run(self) -> None:
        self._print_welcome()

        while True:
            try:
                if self.service.current_user:
                    prompt = f"\n[{self.service.current_user.name}@store] $ "
                else:
                    prompt = "\n[guest@store] $ "

                cmd_line = input(prompt).strip()

                if not cmd_line:
                    continue

                parts = cmd_line.split(maxsplit=1)
                cmd = parts[0].lower()
                args = parts[1] if len(parts) > 1 else ""

                if cmd in self.commands:
                    self.commands[cmd](args)
                else:
                    print(f"  [ОШИБКА] Неизвестная команда: {cmd}")
                    print(f"  [СПРАВКА] Введите 'help' для списка доступных команд")

            except KeyboardInterrupt:
                print("\n\n  До свидания!")
                break
            except Exception as e:
                print(f"  [ОШИБКА] Непредвиденная ошибка: {e}")

    def _print_welcome(self) -> None:
        print("=" * 60)
        print("  ДОБРО ПОЖАЛОВАТЬ В ИНТЕРНЕТ-МАГАЗИН ОДЕЖДЫ")
        print("=" * 60)
        print("  Команды:")
        print("    * help - показать список команд")
        print("    * register - зарегистрироваться")
        print("    * login - войти в систему")
        print("    * list - показать все товары")
        print("  [СПРАВКА] Введите 'help' для полного списка команд")
        print("=" * 60)

    def _show_help(self, args: str) -> None:
        print("\n" + "=" * 70)
        print("  ДОСТУПНЫЕ КОМАНДЫ")
        print("=" * 70)

        print("\n  [АУТЕНТИФИКАЦИЯ]:")
        print("    register <email> <name> <password>  - регистрация нового пользователя")
        print("    login <email> <password>            - вход в систему")
        print("    logout                              - выход из системы")
        print("    whoami                              - информация о текущем пользователе")

        print("\n  [ТОВАРЫ]:")
        print("    list [category]                     - показать все товары")
        print("    search <запрос>                     - поиск товаров по названию")
        print("    info <product_id>                   - подробная информация о товаре")

        print("\n  [КОРЗИНА]:")
        print("    cart                                - показать содержимое корзины")
        print("    add <product_id> [quantity]         - добавить товар в корзину")
        print("    remove <product_id>                 - удалить товар из корзины")
        print("    update <product_id> <quantity>      - изменить количество товара")
        print("    clear                               - очистить корзину")

        print("\n  [ЗАКАЗЫ]:")
        print("    checkout <адрес> [промокод]         - оформить заказ")
        print("    pay <order_id>                      - оплатить заказ")
        print("    orders                              - показать список заказов")
        print("    order <order_id>                    - детали заказа")
        print("    track <order_id>                    - отследить доставку")
        print("    return <order_id>                   - вернуть заказ")

        print("\n  [ОТЗЫВЫ]:")
        print("    review <product_id> <rating> <текст> - оставить отзыв о товаре")

        print("\n  [АДМИНИСТРИРОВАНИЕ]:")
        print("    add_product <название> <цена> <категория> <кол-во> - добавить товар")
        print("    add_promo <код> <скидка%> <дней>   - добавить промокод")

        print("\n  [ОБЩИЕ]:")
        print("    help                                - показать эту справку")
        print("    exit / quit                         - выход из программы")
        print("=" * 70)

    def _exit(self, args: str) -> None:
        print("\n  До свидания! Спасибо за покупки!")
        sys.exit(0)

    def _register(self, args: str) -> None:
        parts = args.split()
        if len(parts) != 3:
            print("  [ОШИБКА] Использование: register <email> <name> <password>")
            print("  [ПРИМЕР] register ivan@mail.ru Иван password123")
            return

        email, name, password = parts

        try:
            user = self.service.register(email, name, password)
            print(f"  [УСПЕХ] Пользователь '{user.name}' успешно зарегистрирован!")
            print(f"  [ИНФО] Теперь вы можете войти с помощью команды: login {email} <пароль>")
        except StoreException as e:
            print(f"  [ОШИБКА] Регистрация: {e}")

    def _login(self, args: str) -> None:
        parts = args.split()
        if len(parts) != 2:
            print("  [ОШИБКА] Использование: login <email> <password>")
            print("  [ПРИМЕР] login ivan@mail.ru password123")
            return

        email, password = parts

        try:
            user = self.service.login(email, password)
            print(f"  [УСПЕХ] Добро пожаловать, {user.name}!")
            print(f"  [ИНФО] Email: {user.email}")
            print(f"  [ИНФО] ID: {user.id}")
        except StoreException as e:
            print(f"  [ОШИБКА] Вход: {e}")

    def _logout(self, args: str) -> None:
        if self.service.current_user:
            name = self.service.current_user.name
            self.service.logout()
            print(f"  [УСПЕХ] До свидания, {name}! Вы вышли из системы.")
        else:
            print("  [ИНФО] Вы не авторизованы")

    def _whoami(self, args: str) -> None:
        if self.service.current_user:
            user = self.service.current_user
            print(f"\n  [ИНФО] Имя: {user.name}")
            print(f"  [ИНФО] Email: {user.email}")
            print(f"  [ИНФО] ID: {user.id}")
            print(f"  [ИНФО] Зарегистрирован: {user.registered_at.strftime('%d.%m.%Y %H:%M')}")
        else:
            print("  [ИНФО] Вы не авторизованы. Используйте 'login' для входа.")

    def _list_products(self, args: str) -> None:
        category = None
        if args:
            category_map = {
                "men": ProductCategory.MEN,
                "women": ProductCategory.WOMEN,
                "kids": ProductCategory.KIDS,
                "accessories": ProductCategory.ACCESSORIES
            }
            category = category_map.get(args.lower())
            if not category:
                print(f"  [ОШИБКА] Неизвестная категория: {args}")
                print("  [СПРАВКА] Доступные категории: men, women, kids, accessories")
                return

        products = self.service.search_products(category=category)

        if not products:
            print("  [ИНФО] Товары не найдены")
            return

        print(f"\n  [СПИСОК ТОВАРОВ] ({len(products)} шт.):")
        print("  " + "-" * 65)
        print(f"  {'ID':<8} {'Название':<25} {'Цена':<10} {'Категория':<12} {'В наличии':<8}")
        print("  " + "-" * 65)

        for p in products:
            print(f"  {p.id[:8]:<8} {p.name[:24]:<25} {p.price:>8.2f} руб.  {p.category.value:<12} {p.stock:<8}")

        print("  " + "-" * 65)
        print(f"  [СПРАВКА] Для просмотра подробной информации: info <product_id>")

    def _search_products(self, args: str) -> None:
        if not args:
            print("  [ОШИБКА] Использование: search <запрос>")
            print("  [ПРИМЕР] search футболка")
            return

        products = self.service.search_products(query=args)

        if not products:
            print(f"  [ИНФО] Товары по запросу '{args}' не найдены")
            return

        print(f"\n  [РЕЗУЛЬТАТЫ ПОИСКА] (по запросу '{args}'):")
        print("  " + "-" * 65)
        print(f"  {'ID':<8} {'Название':<25} {'Цена':<10} {'Категория':<12} {'В наличии':<8}")
        print("  " + "-" * 65)

        for p in products:
            print(f"  {p.id[:8]:<8} {p.name[:24]:<25} {p.price:>8.2f} руб.  {p.category.value:<12} {p.stock:<8}")

        print("  " + "-" * 65)

    def _product_info(self, args: str) -> None:
        if not args:
            print("  [ОШИБКА] Использование: info <product_id>")
            print("  [ПРИМЕР] info abc123")
            return

        product_id = args.strip()
        product = self.service.get_product_by_id(product_id)

        if not product:
            print(f"  [ОШИБКА] Товар с ID '{product_id}' не найден")
            return

        print(f"\n  [ИНФОРМАЦИЯ О ТОВАРЕ]")
        print("  " + "=" * 50)
        print(f"  ID: {product.id}")
        print(f"  Название: {product.name}")
        print(f"  Описание: {product.description}")
        print(f"  Цена: {product.price:.2f} руб.")
        print(f"  Категория: {product.category.value}")
        print(f"  В наличии: {product.stock} шт.")
        print(f"  Продавец ID: {product.seller_id}")
        print(f"  Добавлен: {product.created_at.strftime('%d.%m.%Y %H:%M')}")
        print("  " + "=" * 50)

    def _show_cart(self, args: str) -> None:
        try:
            cart = self.service.view_cart()

            if not cart.items:
                print("  [ИНФО] Ваша корзина пуста")
                print("  [СПРАВКА] Добавьте товары командой: add <product_id> [quantity]")
                return

            print(f"\n  [ВАША КОРЗИНА]")
            print("  " + "-" * 60)
            print(f"  {'Название':<30} {'Кол-во':<8} {'Цена':<10} {'Сумма':<10}")
            print("  " + "-" * 60)

            for item in cart.items:
                subtotal = item.product.price * item.quantity
                print(
                    f"  {item.product.name[:29]:<30} {item.quantity:<8} {item.product.price:>7.2f} руб.  {subtotal:>7.2f} руб.")

            print("  " + "-" * 60)
            print(f"  ИТОГО: {cart.get_total():.2f} руб.")
            print("  " + "-" * 60)
            print(f"  [СПРАВКА] Оформить заказ: checkout <адрес> [промокод]")

        except NotAuthenticatedError as e:
            print(f"  [ОШИБКА] {e}")
            print("  [СПРАВКА] Зарегистрируйтесь или войдите в систему")
        except StoreException as e:
            print(f"  [ОШИБКА] {e}")

    def _add_to_cart(self, args: str) -> None:
        parts = args.split()
        if len(parts) < 1:
            print("  [ОШИБКА] Использование: add <product_id> [quantity]")
            print("  [ПРИМЕР] add abc123 2")
            return

        product_id = parts[0]
        quantity = int(parts[1]) if len(parts) > 1 else 1

        try:
            self.service.add_to_cart(product_id, quantity)
            print(f"  [УСПЕХ] Товар добавлен в корзину (x{quantity})")
            print(f"  [СПРАВКА] Просмотр корзины: cart")
        except NotAuthenticatedError as e:
            print(f"  [ОШИБКА] {e}")
            print("  [СПРАВКА] Зарегистрируйтесь или войдите в систему")
        except ProductNotFoundError as e:
            print(f"  [ОШИБКА] {e}")
            print("  [СПРАВКА] Проверьте ID товара командой 'list'")
        except InsufficientStockError as e:
            print(f"  [ОШИБКА] {e}")
        except ValidationError as e:
            print(f"  [ОШИБКА] {e}")
        except StoreException as e:
            print(f"  [ОШИБКА] {e}")

    def _remove_from_cart(self, args: str) -> None:
        if not args:
            print("  [ОШИБКА] Использование: remove <product_id>")
            print("  [ПРИМЕР] remove abc123")
            return

        try:
            self.service.remove_from_cart(args.strip())
            print(f"  [УСПЕХ] Товар удалён из корзины")
            print(f"  [СПРАВКА] Просмотр корзины: cart")
        except NotAuthenticatedError as e:
            print(f"  [ОШИБКА] {e}")
        except StoreException as e:
            print(f"  [ОШИБКА] {e}")

    def _update_cart(self, args: str) -> None:
        parts = args.split()
        if len(parts) != 2:
            print("  [ОШИБКА] Использование: update <product_id> <quantity>")
            print("  [ПРИМЕР] update abc123 5")
            return

        product_id, quantity_str = parts

        try:
            quantity = int(quantity_str)
            self.service.update_cart_quantity(product_id, quantity)

            if quantity <= 0:
                print(f"  [УСПЕХ] Товар удалён из корзины")
            else:
                print(f"  [УСПЕХ] Количество товара изменено на {quantity}")
            print(f"  [СПРАВКА] Просмотр корзины: cart")

        except ValueError:
            print("  [ОШИБКА] Количество должно быть числом")
        except NotAuthenticatedError as e:
            print(f"  [ОШИБКА] {e}")
        except StoreException as e:
            print(f"  [ОШИБКА] {e}")

    def _clear_cart(self, args: str) -> None:
        try:
            cart = self.service.view_cart()
            if not cart.items:
                print("  [ИНФО] Корзина уже пуста")
                return

            item_count = cart.get_items_count()
            cart.clear()
            print(f"  [УСПЕХ] Корзина очищена (удалено {item_count} товаров)")

        except NotAuthenticatedError as e:
            print(f"  [ОШИБКА] {e}")
        except StoreException as e:
            print(f"  [ОШИБКА] {e}")

    def _checkout(self, args: str) -> None:
        parts = args.split(maxsplit=1)
        if len(parts) < 1:
            print("  [ОШИБКА] Использование: checkout <адрес> [промокод]")
            print("  [ПРИМЕР] checkout 'г. Москва, ул. Ленина 1' WELCOME10")
            return

        address = parts[0]
        promo_code = parts[1] if len(parts) > 1 else None

        try:
            order = self.service.create_order(address, promo_code)

            print(f"\n  [УСПЕХ] ЗАКАЗ УСПЕШНО ОФОРМЛЕН!")
            print("  " + "-" * 50)
            print(f"  Номер заказа: {order.id}")
            print(f"  Сумма заказа: {order.total_amount:.2f} руб.")
            print(f"  Дата заказа: {order.created_at.strftime('%d.%m.%Y %H:%M')}")
            print(f"  Адрес доставки: {address}")
            print("  " + "-" * 50)
            print(f"  [СПРАВКА] Оплатить заказ: pay {order.id}")
            print(f"  [СПРАВКА] Отследить доставку: track {order.id}")

        except NotAuthenticatedError as e:
            print(f"  [ОШИБКА] {e}")
            print("  [СПРАВКА] Зарегистрируйтесь или войдите в систему")
        except CartEmptyError as e:
            print(f"  [ОШИБКА] {e}")
            print("  [СПРАВКА] Добавьте товары командой 'add'")
        except InsufficientStockError as e:
            print(f"  [ОШИБКА] {e}")
        except StoreException as e:
            print(f"  [ОШИБКА] {e}")

    def _pay_order(self, args: str) -> None:
        if not args:
            print("  [ОШИБКА] Использование: pay <order_id>")
            print("  [ПРИМЕР] pay abc123")
            return

        order_id = args.strip()

        try:
            self.service.pay_order(order_id)
            print(f"  [УСПЕХ] ЗАКАЗ УСПЕШНО ОПЛАЧЕН!")
            print(f"  [СПРАВКА] Отследить доставку: track {order_id}")

        except NotAuthenticatedError as e:
            print(f"  [ОШИБКА] {e}")
        except OrderNotFoundError as e:
            print(f"  [ОШИБКА] {e}")
            print("  [СПРАВКА] Проверьте ID заказа командой 'orders'")
        except OrderCannotBePaidError as e:
            print(f"  [ОШИБКА] {e}")
        except StoreException as e:
            print(f"  [ОШИБКА] {e}")

    def _show_orders(self, args: str) -> None:
        try:
            orders = self.service.get_user_orders()

            if not orders:
                print("  [ИНФО] У вас нет заказов")
                print("  [СПРАВКА] Оформите заказ командой 'checkout'")
                return

            print(f"\n  [ВАШИ ЗАКАЗЫ] ({len(orders)} шт.):")
            print("  " + "-" * 70)
            print(f"  {'ID':<8} {'Дата':<20} {'Сумма':<12} {'Статус':<15} {'Оплачен':<10}")
            print("  " + "-" * 70)

            for order in orders:
                paid_status = "Да" if order.payment and order.payment.status.value == "Оплачено" else "Нет"
                print(f"  {order.id[:8]:<8} {order.created_at.strftime('%d.%m.%Y %H:%M'):<20} "
                      f"{order.total_amount:>9.2f} руб.  {order.status.value:<15} {paid_status:<10}")

            print("  " + "-" * 70)
            print(f"  [СПРАВКА] Детали заказа: order <order_id>")

        except NotAuthenticatedError as e:
            print(f"  [ОШИБКА] {e}")
        except StoreException as e:
            print(f"  [ОШИБКА] {e}")

    def _order_details(self, args: str) -> None:
        if not args:
            print("  [ОШИБКА] Использование: order <order_id>")
            print("  [ПРИМЕР] order abc123")
            return

        order_id = args.strip()
        order = self.service.get_order_by_id(order_id)

        if not order:
            print(f"  [ОШИБКА] Заказ с ID '{order_id}' не найден")
            return

        if not self.service.current_user or order.user_id != self.service.current_user.id:
            print(f"  [ОШИБКА] Заказ '{order_id}' не принадлежит вам")
            return

        print(f"\n  [ДЕТАЛИ ЗАКАЗА] #{order.id}")
        print("  " + "=" * 60)
        print(f"  Дата заказа: {order.created_at.strftime('%d.%m.%Y %H:%M')}")
        print(f"  Сумма заказа: {order.total_amount:.2f} руб.")
        print(f"  Статус заказа: {order.status.value}")

        if order.payment:
            print(f"  Статус оплаты: {order.payment.status.value}")
            if order.payment.paid_at:
                print(f"  Оплачен: {order.payment.paid_at.strftime('%d.%m.%Y %H:%M')}")

        if order.delivery:
            print(f"  Статус доставки: {order.delivery.status.value}")
            if order.delivery.tracking_number:
                print(f"  Трек-номер: {order.delivery.tracking_number}")
            if order.delivery.address:
                print(f"  Адрес доставки: {order.delivery.address}")

        print(f"\n  [ТОВАРЫ В ЗАКАЗЕ]:")
        print("  " + "-" * 60)
        print(f"  {'Название':<30} {'Кол-во':<8} {'Цена':<10} {'Сумма':<10}")
        print("  " + "-" * 60)

        for item in order.items:
            subtotal = item.product.price * item.quantity
            print(
                f"  {item.product.name[:29]:<30} {item.quantity:<8} {item.product.price:>7.2f} руб.  {subtotal:>7.2f} руб.")

        print("  " + "-" * 60)
        print(f"  [СПРАВКА] Отследить доставку: track {order.id}")
        if order.can_return():
            print(f"  [СПРАВКА] Вернуть заказ: return {order.id}")
        print("  " + "=" * 60)

    def _track_delivery(self, args: str) -> None:
        if not args:
            print("  [ОШИБКА] Использование: track <order_id>")
            print("  [ПРИМЕР] track abc123")
            return

        order_id = args.strip()

        try:
            delivery = self.service.track_delivery(order_id)
            order = self.service.get_order_by_id(order_id)

            print(f"\n  [ИНФОРМАЦИЯ О ДОСТАВКЕ]")
            print("  " + "=" * 50)
            print(f"  Заказ: {order_id}")
            print(f"  Статус: {delivery.status.value}")
            print(f"  Адрес: {delivery.address}")

            if delivery.tracking_number:
                print(f"  Трек-номер: {delivery.tracking_number}")
            if delivery.shipped_at:
                print(f"  Отправлен: {delivery.shipped_at.strftime('%d.%m.%Y %H:%M')}")
            if delivery.delivered_at:
                print(f"  Доставлен: {delivery.delivered_at.strftime('%d.%m.%Y %H:%M')}")
            if order:
                print(f"  Статус заказа: {order.status.value}")

            print("  " + "=" * 50)

        except NotAuthenticatedError as e:
            print(f"  [ОШИБКА] {e}")
        except OrderNotFoundError as e:
            print(f"  [ОШИБКА] {e}")
        except StoreException as e:
            print(f"  [ОШИБКА] {e}")

    def _return_order(self, args: str) -> None:
        if not args:
            print("  [ОШИБКА] Использование: return <order_id>")
            print("  [ПРИМЕР] return abc123")
            return

        order_id = args.strip()

        try:
            order = self.service.request_return(order_id)
            print(f"  [УСПЕХ] ЗАКАЗ ВОЗВРАЩЁН!")
            print(f"  [ИНФО] Деньги будут возвращены на карту в течение 3-5 дней")
            print(f"  [ИНФО] Статус заказа: {order.status.value}")

        except NotAuthenticatedError as e:
            print(f"  [ОШИБКА] {e}")
        except OrderNotFoundError as e:
            print(f"  [ОШИБКА] {e}")
        except OrderCannotBeReturnedError as e:
            print(f"  [ОШИБКА] {e}")
            print("  [СПРАВКА] Возврат возможен только для доставленных заказов")
        except StoreException as e:
            print(f"  [ОШИБКА] {e}")

    def _add_review(self, args: str) -> None:
        parts = args.split(maxsplit=2)
        if len(parts) < 3:
            print("  [ОШИБКА] Использование: review <product_id> <rating> <текст>")
            print("  [ПРИМЕР] review abc123 5 Отличный товар!")
            return

        product_id = parts[0]

        try:
            rating = int(parts[1])
            comment = parts[2]

            review = self.service.add_review(product_id, rating, comment)

            print(f"  [УСПЕХ] Отзыв добавлен!")
            print(f"  [ИНФО] Оценка: {rating}/5")
            print(f"  [ИНФО] Комментарий: {comment}")

        except ValueError:
            print("  [ОШИБКА] Оценка должна быть числом от 1 до 5")
        except NotAuthenticatedError as e:
            print(f"  [ОШИБКА] {e}")
            print("  [СПРАВКА] Зарегистрируйтесь или войдите в систему")
        except ProductNotFoundError as e:
            print(f"  [ОШИБКА] {e}")
        except InvalidRatingError as e:
            print(f"  [ОШИБКА] {e}")
        except StoreException as e:
            print(f"  [ОШИБКА] {e}")

    def _add_product_admin(self, args: str) -> None:
        parts = args.split()
        if len(parts) < 4:
            print("  [ОШИБКА] Использование: add_product <название> <цена> <категория> <количество>")
            print("  [СПРАВКА] Категории: men, women, kids, accessories")
            print("  [ПРИМЕР] add_product 'Новая куртка' 5000 men 10")
            return

        try:
            price = float(parts[-3])
            category_str = parts[-2].lower()
            stock = int(parts[-1])
            name = " ".join(parts[:-3])
        except (ValueError, IndexError):
            print("  [ОШИБКА] Неверный формат команды")
            print("  [ПРИМЕР] add_product 'Новая куртка' 5000 men 10")
            return

        category_map = {
            "men": ProductCategory.MEN,
            "women": ProductCategory.WOMEN,
            "kids": ProductCategory.KIDS,
            "accessories": ProductCategory.ACCESSORIES
        }

        category = category_map.get(category_str)
        if not category:
            print(f"  [ОШИБКА] Неизвестная категория: {category_str}")
            print("  [СПРАВКА] Доступные категории: men, women, kids, accessories")
            return

        try:
            if not self.service.sellers:
                seller = self.service.add_seller("Администратор", "admin@store.ru")
            else:
                seller = self.service.sellers[0]

            product = self.service.add_product(
                name=name, description="", price=price, category=category,
                seller_id=seller.id, stock=stock
            )

            print(f"  [УСПЕХ] Товар успешно добавлен!")
            print(f"  ID: {product.id}")
            print(f"  Название: {product.name}")
            print(f"  Цена: {product.price:.2f} руб.")
            print(f"  Категория: {product.category.value}")
            print(f"  В наличии: {product.stock} шт.")

        except ValidationError as e:
            print(f"  [ОШИБКА] {e}")
        except StoreException as e:
            print(f"  [ОШИБКА] {e}")

    def _add_promo_admin(self, args: str) -> None:
        parts = args.split()
        if len(parts) != 3:
            print("  [ОШИБКА] Использование: add_promo <код> <скидка%> <дней>")
            print("  [ПРИМЕР] add_promo SUMMER20 20 30")
            return

        code = parts[0]

        try:
            discount = float(parts[1])
            days = int(parts[2])

            if discount <= 0 or discount > 100:
                print("  [ОШИБКА] Скидка должна быть от 1 до 100 процентов")
                return
            if days <= 0:
                print("  [ОШИБКА] Срок действия должен быть положительным числом")
                return

            expires_at = datetime.now() + timedelta(days=days)
            promo = self.service.add_promo_code(code, discount, expires_at)

            print(f"  [УСПЕХ] Промокод успешно добавлен!")
            print(f"  Код: {promo.code}")
            print(f"  Скидка: {promo.discount_percent}%")
            print(f"  Действует до: {expires_at.strftime('%d.%m.%Y')}")

        except ValueError:
            print("  [ОШИБКА] Неверный формат: скидка и дни должны быть числами")
        except ValidationError as e:
            print(f"  [ОШИБКА] {e}")
        except StoreException as e:
            print(f"  [ОШИБКА] {e}")


def main():
    cli = ClothingStoreCLI()
    cli.run()


if __name__ == "__main__":
    main()