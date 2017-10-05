from outsource.user_views import *
from django.conf.urls import url,include
from rest_framework import routers


urlpatterns = [
    url(r'^social-api-auth/', ObtainJSONWebToken.as_view()),
    url(r'^rest-api/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^user-manage/',UserManageViewSet.as_view({'get': 'list','put':'update','post':'create'})),

    url(r'^get_cafe_beverage/(?P<cafe_pk>\d+)', CafeBeverageList.as_view({'get':'retrieve'})),
    url(r'^reservation_page/',CafeBeverageList.as_view({'get':'list'})),

    url(r'^get_favorite_cafe/',UsersFavoriteCafe.as_view({'get':'list'})),
    url(r'^add_favorite_cafe/(?P<cafe_pk>\d+)',UsersFavoriteCafe.as_view({'post': 'update'})),

    url(r'^get_all_coupons/',CouponViewSet.as_view({'get':'list'})),
    url(r'^get_one_coupon/(?P<pk>\d+)',CouponViewSet.as_view({'get':'retrieve'})),

    url(r'^order_beverage/(?P<cafe_pk>\d+)',OrderViewSet.as_view({'post':'create'})),
    url(r'^recent_payment_list_by_order/(?P<coupon_pk>\d+)',OrderViewSet.as_view({'get':'retrieve'})),
    url(r'^recent_payment_list_by_id/',OrderViewSet.as_view({'get':'list'})),

    url(r'^get_events/(?P<cafe_pk>\d+)',EventViewSet.as_view({'get':'list'})),
]
