from outsource.cafe_views import *
from django.conf.urls import url
urlpatterns = [
    url(r'^get_orders/',OrderViewSet.as_view({'get':'list'})),
    url(r'^delete_order/(?P<pk>\d+)',OrderViewSet.as_view({'delete':'destroy'})),
    url(r'^complete_order/(?P<pk>\d+)',OrderViewSet.as_view({'post':'update'})),
    url(r'^create_event/', EventViewSet.as_view({'post':'create'})),
    url(r'^get_my_events/', EventViewSet.as_view({'get':'list'})),
    url(r'^broadcast_advertise/(?P<beverage_pk>\d+)', BroadCastAdvertise.as_view()),
    url(r'^set_open/', CafeOpenUpdate.as_view()),
]