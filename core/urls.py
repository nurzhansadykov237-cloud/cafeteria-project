from django.urls import path
from django.contrib.auth import views as auth_views
from . import views


app_name = "core"

urlpatterns = [
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
]