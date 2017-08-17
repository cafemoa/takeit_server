from outsource.views import *
from django.conf.urls import url,include
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework import routers
from outsource.views import DeviceViewSet

router = routers.DefaultRouter()
router.register(r'devices', DeviceViewSet)

urlpatterns = [
    url(r'^fcm/', include(router.urls)),
    url('^', include('outsource.cafe_urls'), name='cafe'),
    url('^', include('outsource.user_urls'), name='user'),
    url(r'^api-auth/', obtain_jwt_token),
    url(r'^payment_complete/', payment_complete, name='payment_complete'),
    url(r'^payment/', payment, name='payment'),
]