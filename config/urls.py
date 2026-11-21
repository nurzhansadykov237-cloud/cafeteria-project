from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from core import views

from django.views.generic import TemplateView

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
    openapi.Info(
        title="Cafeteria API",
        default_version="v1",
        description="API проекта Столовая: меню и предзаказ",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [

    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('order/', views.create_order, name='create_order'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/remove/<int:dish_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:dish_id>/', views.update_cart, name='update_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('cart/add/<int:dish_id>/', views.add_to_cart, name='add_to_cart'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(
        template_name='core/login.html'
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('dishes/', views.DishListView.as_view(), name='dish_list'),
    path('dishes/<int:pk>/', views.DishDetailView.as_view(), name='dish_detail'),
    path('dishes/add/', views.DishCreateView.as_view(), name='dish_create'),
    path('dishes/<int:pk>/edit/', views.DishUpdateView.as_view(), name='dish_update'),
    path('dishes/<int:pk>/delete/', views.DishDeleteView.as_view(), name='dish_delete'),

    path('statistics/', views.StatisticsView.as_view(), name='statistics'),

    # REST API
    path('api/', include('core.api_urls')),

    # Swagger и ReDoc
    path('api/docs/', schema_view.with_ui(
        'swagger', cache_timeout=0
    ), name='schema-swagger-ui'),

    path('api/redoc/', schema_view.with_ui(
        'redoc', cache_timeout=0
    ), name='schema-redoc'),
]