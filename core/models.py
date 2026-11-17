
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название категории")
    description = models.TextField(blank=True, verbose_name="Описание")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"


class Dish(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="dishes",
        verbose_name="Категория"
    )
    name = models.CharField(max_length=150, verbose_name="Название блюда")
    description = models.TextField(blank=True, verbose_name="Описание")
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Цена")
    is_available = models.BooleanField(default=True, verbose_name="Доступно")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Блюдо"
        verbose_name_plural = "Блюда"
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["category", "is_available"]),
        ]


class DailyMenu(models.Model):
    date = models.DateField(unique=True, verbose_name="Дата меню")
    dishes = models.ManyToManyField(
        Dish,
        related_name="daily_menus",
        verbose_name="Блюда"
    )

    def __str__(self):
        return f"Меню на {self.date}"

    class Meta:
        verbose_name = "Меню дня"
        verbose_name_plural = "Меню дня"


class Order(models.Model):
    STATUS_CHOICES = [
        ("new", "Новый"),
        ("preparing", "Готовится"),
        ("completed", "Выполнен"),
        ("cancelled", "Отменён"),
    ]

    customer_name = models.CharField(max_length=150, verbose_name="Имя заказчика")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата заказа")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="new",
        verbose_name="Статус"
    )

    def __str__(self):
        return f"Заказ №{self.id} — {self.customer_name}"

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Заказ"
    )
    dish = models.ForeignKey(
        Dish,
        on_delete=models.PROTECT,
        verbose_name="Блюдо"
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Цена на момент заказа")

    def __str__(self):
        return f"{self.dish.name} x {self.quantity}"

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказа"
