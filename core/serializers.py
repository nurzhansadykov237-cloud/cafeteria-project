from rest_framework import serializers
from .models import Dish, DailyMenu, Order, OrderItem


class DishSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(
        source="category.name",
        read_only=True
    )

    class Meta:
        model = Dish
        fields = "__all__"


class DailyMenuSerializer(serializers.ModelSerializer):
    dishes = DishSerializer(many=True, read_only=True)

    class Meta:
        model = DailyMenu
        fields = "__all__"


class OrderItemSerializer(serializers.ModelSerializer):
    dish_name = serializers.CharField(
        source="dish.name",
        read_only=True
    )

    class Meta:
        model = OrderItem
        fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = "__all__"