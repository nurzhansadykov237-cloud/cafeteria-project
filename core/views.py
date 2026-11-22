
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction
from .models import Category, Dish, DailyMenu, Order, OrderItem
from django.db.models import Q
from django.db.models import Count, Sum, F, DecimalField
from django.core.paginator import Paginator
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .forms import DishForm


def home(request):
    categories = Category.objects.all()
    dishes = Dish.objects.filter(
        is_available=True
    ).select_related("category")

    today_menu = DailyMenu.objects.filter(
        date__gte=__import__("datetime").date.today()
    ).order_by("date").first()

    if today_menu:
        dishes = today_menu.dishes.filter(
            is_available=True
        ).select_related("category")

    selected_category = request.GET.get("category")
    if selected_category:
        dishes = dishes.filter(category_id=selected_category)

    search = request.GET.get("search")
    if search:
        dishes = dishes.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search)
        )

    sort = request.GET.get("sort")
    if sort == "price":
        dishes = dishes.order_by("price")
    elif sort == "-price":
        dishes = dishes.order_by("-price")
    else:
        dishes = dishes.order_by("name")

    paginator = Paginator(dishes, 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "core/index.html", {
        "categories": categories,
        "dishes": page_obj,
        "today_menu": today_menu,
        "page_obj": page_obj,
        "selected_category": selected_category,
        "search": search,
        "sort": sort,
    })


def create_order(request):
    if request.method == "POST":
        customer_name = request.POST.get("customer_name", "").strip()
        dish_ids = request.POST.getlist("dishes")

        if not customer_name:
            messages.error(request, "Введите ваше имя.")
            return redirect("core:home")

        if not dish_ids:
            messages.error(request, "Выберите хотя бы одно блюдо.")
            return redirect("core:home")

        selected_dishes = Dish.objects.filter(
            id__in=dish_ids,
            is_available=True
        )

        if selected_dishes.count() != len(set(dish_ids)):
            messages.error(request, "Некоторые блюда недоступны.")
            return redirect("core:home")

        with transaction.atomic():
            order = Order.objects.create(customer_name=customer_name)

            for dish in selected_dishes:
                quantity = int(request.POST.get(f"quantity_{dish.id}", 1))

                OrderItem.objects.create(
                    order=order,
                    dish=dish,
                    quantity=quantity,
                    price=dish.price
                )

            total = sum(
                item.price * item.quantity
                for item in order.items.all()
            )

        return redirect(f"/?success={order.id}&total={total}")

    return redirect("core:home")


from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("core:home")
    else:
        form = UserCreationForm()

    return render(request, "core/register.html", {
        "form": form
    })


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return (
            self.request.user.is_superuser
            or self.request.user.groups.filter(
                name="Администратор"
            ).exists()
        )


class DishListView(StaffRequiredMixin, ListView):
    model = Dish
    template_name = "core/dish_list.html"
    context_object_name = "dishes"


class DishDetailView(StaffRequiredMixin, DetailView):
    model = Dish
    template_name = "core/dish_detail.html"


class DishCreateView(StaffRequiredMixin, CreateView):
    model = Dish
    form_class = DishForm
    template_name = "core/dish_form.html"
    success_url = reverse_lazy("core:dish_list")


class DishUpdateView(StaffRequiredMixin, UpdateView):
    model = Dish
    form_class = DishForm
    template_name = "core/dish_form.html"
    success_url = reverse_lazy("core:dish_list")


class DishDeleteView(StaffRequiredMixin, DeleteView):
    model = Dish
    template_name = "core/dish_confirm_delete.html"
    success_url = reverse_lazy("core:dish_list")


class StatisticsView(StaffRequiredMixin, TemplateView):
    template_name = "core/statistics.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        from django.utils import timezone

        today = timezone.localdate()

        # Общая статистика
        context["dishes_count"] = Dish.objects.count()
        context["orders_count"] = Order.objects.count()

        context["total_revenue"] = OrderItem.objects.aggregate(
            total=Sum(F("price") * F("quantity"))
        )["total"] or 0

        context["top_dishes"] = (
            OrderItem.objects.values("dish__name")
            .annotate(total_quantity=Sum("quantity"))
            .order_by("-total_quantity")[:5]
        )

        # Отчёт за сегодня
        context["today"] = today

        context["daily_orders_count"] = Order.objects.filter(
            created_at__date=today
        ).count()

        context["daily_revenue"] = OrderItem.objects.filter(
            order__created_at__date=today
        ).aggregate(
            total=Sum(F("price") * F("quantity"))
        )["total"] or 0

        context["daily_top_dishes"] = (
            OrderItem.objects.filter(
                order__created_at__date=today
            )
            .values("dish__name")
            .annotate(total_quantity=Sum("quantity"))
            .order_by("-total_quantity")[:5]
        )

        return context


from rest_framework import viewsets, permissions
from .serializers import (
    DishSerializer,
    DailyMenuSerializer,
    OrderSerializer,
)


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated

        return (
            request.user
            and request.user.is_authenticated
            and (
                request.user.is_superuser
                or request.user.groups.filter(
                    name="Администратор"
                ).exists()
            )
        )


class DishViewSet(viewsets.ModelViewSet):
    queryset = Dish.objects.select_related("category")
    serializer_class = DishSerializer
    permission_classes = [IsAdminOrReadOnly]


class DailyMenuViewSet(viewsets.ModelViewSet):
    queryset = DailyMenu.objects.prefetch_related("dishes__category")
    serializer_class = DailyMenuSerializer
    permission_classes = [IsAdminOrReadOnly]


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.prefetch_related("items__dish")
    serializer_class = OrderSerializer
    permission_classes = [IsAdminOrReadOnly]


def about(request):
    return render(request, "core/about.html")


def cart_view(request):
    cart = request.session.get("cart", {})
    dishes = Dish.objects.filter(
        id__in=cart.keys(),
        is_available=True
    )

    cart_items = []
    total = 0
    valid_cart = {}

    for dish in dishes:
        try:
            quantity = int(cart.get(str(dish.id), 0))
        except (ValueError, TypeError):
            continue

        if quantity < 1:
            continue

        valid_cart[str(dish.id)] = quantity

        subtotal = dish.price * quantity
        total += subtotal

        cart_items.append({
            "dish": dish,
            "quantity": quantity,
            "subtotal": subtotal,
        })

    if valid_cart != cart:
        request.session["cart"] = valid_cart
        messages.warning(
            request,
            "Некорректные позиции корзины были удалены."
        )

    return render(request, "core/cart.html", {
        "cart_items": cart_items,
        "total": total,
    })


def add_to_cart(request, dish_id):
    if request.method == "POST":
        dish = Dish.objects.filter(
            id=dish_id,
            is_available=True
        ).first()

        if dish is None:
            messages.error(request, "Блюдо недоступно.")
            return redirect("core:home")

        try:
            quantity = int(request.POST.get("quantity", 1))
        except (ValueError, TypeError):
            messages.error(request, "Введите корректное количество.")
            return redirect("core:home")

        if quantity < 1:
            messages.error(request, "Количество должно быть больше нуля.")
            return redirect("core:home")

        cart = request.session.get("cart", {})
        key = str(dish_id)

        cart[key] = cart.get(key, 0) + quantity

        request.session["cart"] = cart

        messages.success(
            request,
            f"«{dish.name}» добавлено в корзину."
        )

    return redirect("core:cart")


def checkout(request):
    if request.method != "POST":
        return redirect("core:cart")

    customer_name = request.POST.get("customer_name", "").strip()
    cart = request.session.get("cart", {})

    if not customer_name:
        messages.error(request, "Введите ваше имя.")
        return redirect("core:cart")

    if not cart:
        messages.error(request, "Корзина пуста.")
        return redirect("core:cart")

    dishes = Dish.objects.filter(
        id__in=cart.keys(),
        is_available=True
    )

    if dishes.count() != len(cart):
        messages.error(request, "Некоторые блюда больше недоступны.")
        return redirect("core:cart")

    quantities = {}

    for dish in dishes:
        try:
            quantity = int(cart[str(dish.id)])
        except (ValueError, TypeError):
            messages.error(request, "Некорректное количество блюд.")
            return redirect("core:cart")

        if quantity < 1:
            messages.error(request, "Количество должно быть больше нуля.")
            return redirect("core:cart")

        quantities[dish.id] = quantity

    with transaction.atomic():
        order = Order.objects.create(
            customer_name=customer_name
        )

        for dish in dishes:
            OrderItem.objects.create(
                order=order,
                dish=dish,
                quantity=quantities[dish.id],
                price=dish.price
            )

    request.session["cart"] = {}

    messages.success(
        request,
        f"Заказ №{order.id} успешно оформлен!"
    )

    return redirect("core:home")


def remove_from_cart(request, dish_id):
    if request.method == "POST":
        cart = request.session.get("cart", {})
        key = str(dish_id)

        if key in cart:
            del cart[key]
            request.session["cart"] = cart
            messages.success(request, "Блюдо удалено из корзины.")
        else:
            messages.error(request, "Блюдо не найдено в корзине.")

    return redirect("core:cart")


def update_cart(request, dish_id):
    if request.method == "POST":
        cart = request.session.get("cart", {})
        key = str(dish_id)

        if key not in cart:
            messages.error(request, "Блюдо не найдено в корзине.")
            return redirect("core:cart")

        try:
            quantity = int(request.POST.get("quantity", 1))
        except (ValueError, TypeError):
            messages.error(request, "Введите корректное количество.")
            return redirect("core:cart")

        if quantity < 1:
            messages.error(request, "Количество должно быть больше нуля.")
            return redirect("core:cart")

        cart[key] = quantity
        request.session["cart"] = cart

        messages.success(request, "Количество блюда обновлено.")

    return redirect("core:cart")
