from rest_framework.routers import DefaultRouter
from .views import DishViewSet, DailyMenuViewSet, OrderViewSet

router = DefaultRouter()

router.register("dishes", DishViewSet)
router.register("menus", DailyMenuViewSet)
router.register("orders", OrderViewSet)

urlpatterns = router.urls