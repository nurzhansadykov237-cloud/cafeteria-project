from django.test import TestCase
from .models import Category, Dish, Order, OrderItem
from .forms import DishForm
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth.models import User

class CategoryModelTest(TestCase):

    def test_category_creation(self):
        category = Category.objects.create(
            name="Тестовая категория",
            description="Проверка категории"
        )

        self.assertEqual(category.name, "Тестовая категория")


class DishModelTest(TestCase):

    def test_dish_creation(self):
        category = Category.objects.create(
            name="Первые блюда"
        )

        dish = Dish.objects.create(
            category=category,
            name="Тестовый борщ",
            description="Проверка блюда",
            price=500,
            is_available=True
        )

        self.assertEqual(dish.name, "Тестовый борщ")
        self.assertEqual(dish.price, 500)
        self.assertTrue(dish.is_available)

class OrderModelTest(TestCase):

    def test_order_creation(self):
        order = Order.objects.create(
            customer_name="Тестовый клиент"
        )

        self.assertEqual(order.customer_name, "Тестовый клиент")

    def test_order_item_creation(self):
        category = Category.objects.create(
            name="Первые блюда"
        )

        dish = Dish.objects.create(
            category=category,
            name="Борщ",
            description="Тестовый борщ",
            price=500,
            is_available=True
        )

        order = Order.objects.create(
            customer_name="Тестовый клиент"
        )

        item = OrderItem.objects.create(
            order=order,
            dish=dish,
            quantity=2,
            price=500
        )

        self.assertEqual(item.quantity, 2)
        self.assertEqual(item.price, 500)

class DishFormTest(TestCase):

    def setUp(self):
        self.category = Category.objects.create(
            name="Тестовая категория"
        )

    def test_valid_dish_form(self):
        form = DishForm(data={
            "category": self.category.id,
            "name": "Куриный суп",
            "description": "Вкусный суп",
            "price": "500.00",
            "is_available": True
        })

        self.assertTrue(form.is_valid())

    def test_invalid_dish_form(self):
        form = DishForm(data={
            "category": self.category.id,
            "name": "",
            "description": "Тест",
            "price": "500.00",
            "is_available": True
        })

        self.assertFalse(form.is_valid())

    def test_zero_price_is_invalid(self):
        form = DishForm(data={
            "category": self.category.id,
            "name": "Бесплатный суп",
            "description": "Тест",
            "price": "0.00",
            "is_available": True
        })

        self.assertFalse(form.is_valid())

    def test_negative_price_is_invalid(self):
        form = DishForm(data={
            "category": self.category.id,
            "name": "Суп с отрицательной ценой",
            "description": "Тест",
            "price": "-100.00",
            "is_available": True
        })

        self.assertFalse(form.is_valid())

class HomeViewTest(TestCase):

    def test_home_page_status_code(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_home_page_contains_title(self):
        response = self.client.get("/")
        self.assertContains(response, "Столовая")

class DishAPITest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="api_test_user",
            password="testpassword123"
        )

        self.category = Category.objects.create(
            name="API категория"
        )

        self.dish = Dish.objects.create(
            category=self.category,
            name="API борщ",
            description="Тестовое блюдо",
            price=500,
            is_available=True
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_authenticated_user_can_view_dishes(self):
        response = self.client.get("/api/dishes/")
        self.assertEqual(response.status_code, 200)

    def test_regular_user_cannot_create_dish(self):
        response = self.client.post(
            "/api/dishes/",
            {
                "name": "Запрещённое блюдо",
                "description": "Тест запрета",
                "price": "300.00",
                "is_available": True,
                "category": self.category.id
            },
            format="json"
        )

        self.assertEqual(response.status_code, 403)

class CartTest(TestCase):

    def setUp(self):
        self.category = Category.objects.create(
            name="Тестовая категория"
        )

        self.dish = Dish.objects.create(
            category=self.category,
            name="Тестовый борщ",
            description="Борщ для проверки корзины",
            price=500,
            is_available=True
        )

    def test_add_dish_to_cart(self):
        response = self.client.post(
            reverse("add_to_cart", args=[self.dish.id]),
            {"quantity": 2}
        )

        self.assertRedirects(response, reverse("cart"))

        cart = self.client.session["cart"]
        self.assertEqual(cart[str(self.dish.id)], 2)

    def test_cart_total(self):
        session = self.client.session
        session["cart"] = {str(self.dish.id): 2}
        session.save()

        response = self.client.get(reverse("cart"))

        self.assertEqual(response.context["total"], 1000)

    def test_update_cart_quantity(self):
        session = self.client.session
        session["cart"] = {str(self.dish.id): 2}
        session.save()

        self.client.post(
            reverse("update_cart", args=[self.dish.id]),
            {"quantity": 5}
        )

        cart = self.client.session["cart"]
        self.assertEqual(cart[str(self.dish.id)], 5)

    def test_remove_dish_from_cart(self):
        session = self.client.session
        session["cart"] = {str(self.dish.id): 2}
        session.save()

        self.client.post(
            reverse("remove_from_cart", args=[self.dish.id])
        )

        cart = self.client.session["cart"]
        self.assertNotIn(str(self.dish.id), cart)

    def test_checkout_creates_order_and_clears_cart(self):
        session = self.client.session
        session["cart"] = {str(self.dish.id): 2}
        session.save()

        response = self.client.post(
            reverse("checkout"),
            {"customer_name": "Тестовый клиент"}
        )

        self.assertEqual(Order.objects.count(), 1)

        order = Order.objects.first()

        self.assertEqual(order.customer_name, "Тестовый клиент")
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.items.first().quantity, 2)

        self.assertEqual(self.client.session["cart"], {})

class CartInvalidQuantityTest(TestCase):

    def setUp(self):
        self.category = Category.objects.create(
            name="Тестовая категория"
        )

        self.dish = Dish.objects.create(
            category=self.category,
            name="Тестовый суп",
            description="Проверка количества",
            price=300,
            is_available=True
        )

    def test_add_to_cart_with_invalid_quantity(self):
        response = self.client.post(
            reverse("add_to_cart", args=[self.dish.id]),
            {"quantity": "abc"}
        )

        self.assertRedirects(response, reverse("home"))
        self.assertNotIn(
            str(self.dish.id),
            self.client.session.get("cart", {})
        )

    def test_checkout_with_invalid_cart_quantity(self):
        session = self.client.session
        session["cart"] = {
            str(self.dish.id): "abc"
        }
        session.save()

        response = self.client.post(
            reverse("checkout"),
            {"customer_name": "Тестовый клиент"}
        )

        self.assertRedirects(response, reverse("cart"))
        self.assertEqual(Order.objects.count(), 0)