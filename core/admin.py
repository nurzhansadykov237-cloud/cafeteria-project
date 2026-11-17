
from django.contrib import admin
from django.http import HttpResponse
from openpyxl import Workbook
from .models import Category, Dish, DailyMenu, Order, OrderItem


def export_dishes_excel(modeladmin, request, queryset):
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Блюда"

    sheet.append(["ID", "Название", "Категория", "Цена", "Доступно"])

    for dish in queryset.select_related("category"):
        sheet.append([
            dish.id,
            dish.name,
            dish.category.name,
            float(dish.price),
            "Да" if dish.is_available else "Нет",
        ])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="dishes.xlsx"'
    workbook.save(response)
    return response


export_dishes_excel.short_description = "Экспорт выбранных блюд в Excel"


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "category", "price", "is_available")
    list_filter = ("category", "is_available")
    search_fields = ("name", "description")
    actions = [export_dishes_excel]


@admin.register(DailyMenu)
class DailyMenuAdmin(admin.ModelAdmin):
    list_display = ("id", "date")
    filter_horizontal = ("dishes",)



@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "customer_name",
        "created_at",
        "status",
        "total_amount",
    )
    list_filter = ("status", "created_at")
    search_fields = ("customer_name",)
    inlines = [OrderItemInline]
    readonly_fields = ("total_amount",)

    @admin.display(description="Общая стоимость")
    def total_amount(self, obj):
        return sum(
            item.price * item.quantity
            for item in obj.items.all()
        )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "dish", "quantity", "price")
    list_filter = ("dish",)
