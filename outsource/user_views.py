from django.shortcuts import render
from outsource.models import *
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
import math
from outsource.serializers import *
from rest_framework import viewsets
from rest_framework.response import Response
from fcm.utils import get_device_model
from rest_framework import status
import datetime
from django.utils import timezone


## 해야할것 : 이벤트를 포함한 결제
## 안드로이드 -> 결제요청(구현필요) -> 결제페이지 -> order_beverage
class UserManageViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserManageSerializer

    def list(self, request): # GET : user-manage
        user = User.objects.get(pk=request.user.pk)
        serializers=UserManageSerializer(user)
        return Response(serializers.data)

    def create(self, request): # POST : user-manage
        serializer=UserManageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request): # PUT : user-manage
        if request.auth == None :
            return Response(status=status.HTTP_400_BAD_REQUEST)
        user=User.objects.get(pk=request.user.pk)

        serializer=UserManageSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
        return Response(status=status.HTTP_201_CREATED)

class CafeBeverageList(viewsets.ModelViewSet):
    queryset=Beverage.objects.all()
    serializer_class = BeverageSerializer

    def retrieve(self, request,cafe_pk): # GET : get_cafe_beverage
        cafe=Cafe.objects.get(pk=cafe_pk)
        queryset=cafe.beverages.all()
        serializer = BeverageSerializer(queryset, many=True)
        return Response(serializer.data)

    def list(self, request): #  GET : reservation_page
        queryset=Cafe.objects.all()
        serializers=CafeFullSerializer(queryset,many=True)
        return Response(serializers.data)

class UsersFavoriteCafe(viewsets.ModelViewSet):
    queryset = Cafe.objects.all()
    serializer_class = CafeSerializer

    def list(self, request):  # GET : get_favorite_cafe
        user = User.objects.get(pk=request.user.pk)
        queryset = user.favorite_cafe.all()
        serializer = CafeSerializer(queryset, many=True)
        return Response(serializer.data)

    def update(self, request,cafe_pk): # POST : add_favorite_cafe
        user = User.objects.get(pk=request.user.pk)
        cafe=Cafe.objects.get(pk=cafe_pk)
        user.favorite_cafe.add(cafe)
        serializer = CafeSerializer(cafe)
        return Response(serializer.data)

class CouponViewSet(viewsets.ModelViewSet):
    queryset = Coupon.objects.all()
    def list(self, request): # GET : get_all_coupon
        user = User.objects.get(pk=request.user.pk)
        queryset=Coupon.objects.filter(user=user).order_by('-last_coupon_update')
        serializers=CouponSerializer(queryset, many=True)
        return Response(serializers.data)

    def retrieve(self, request, pk): # GET : get_one_coupon
        queryset = Coupon.objects.get(pk=pk)
        serializer=CouponSerializer(queryset)
        return Response(serializer.data)

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    def create(self,request,cafe_pk): #  POST : order_beverage
        user = User.objects.get(pk=request.user.pk)
        cafe=Cafe.objects.get(pk=cafe_pk)
        serializer=OrderSerializer(data=request.data)

        last_order = Order.objects.filter(cafe=cafe)

        if last_order.count()==0 :
            order_num = 0

        else:
            last_order = last_order.order_by('-order_time').first()
            last_order_date = last_order.order_time.date()
            now_order_date = timezone.now().today().date()
            if last_order_date == now_order_date:
                order_num = last_order.order_num + 1
            else:
                order_num = 0


        if serializer.is_valid():
            order=serializer.save(orderer_id=request.user.pk,cafe_id=cafe_pk,order_num=order_num)
            cafe.current_order_num += 1
            cafe.save()

            options = request.data.get('options')
            amount_price=0
            for option_info in options:
                option=BeverageOption.objects.create(beverage_id=option_info['beverage'],is_ice=option_info['is_ice'],
                                                     size=option_info['size'],whipping_cream=option_info['whipping_cream'], shot_num=option_info['shot_num'])

                option.save()
                order.options.add(option)
                size_price=option.beverage.price.split()
                price=size_price[option_info['size']]
                price=int(price.split(':')[1])
                amount_price += price

            order.amount_price=amount_price
            order.save()

            Device = get_device_model()
            cafeDevice = Device.objects.filter(user=cafe)
            if not cafeDevice.count()==0 :
                cafeDevice=cafeDevice.first()
                cafeDevice.send_message({'message': '음료가 주문되었습니다!'}, collapse_key="음료가 주문되었습니다!")
            if cafe.can_use_coupon :
                if order.payment_type==0 :
                    coupon = Coupon.objects.filter(cafe=order.cafe, user=user)
                    if coupon.count() == 0:
                        coupon = Coupon.objects.create(cafe=order.cafe, user=user)
                    else:
                        coupon = coupon.first()

                    coupon.coupon_progress += len(options)
                    coupon.last_coupon_update = timezone.now()
                    coupon.save()



            serializer = OrderSerializer(order)
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.data,status=status.HTTP_400_BAD_REQUEST)

    def list(self, request): # GET : recent_payment_list_by_id
        user=User.objects.get(pk=request.user.pk)
        queryset = Order.objects.filter(orderer=user, is_done=True).order_by('-order_time')
        serializer = OrderSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self,request,coupon_pk): # GET : recent_payment_list_by_order
        coupon = Coupon.objects.get(pk=coupon_pk)
        queryset = Order.objects.filter(orderer=coupon.user, cafe=coupon.cafe, is_done=True).order_by('-order_time')
        serializer = OrderSerializer(queryset, many=True)
        return Response(serializer.data)


class EventViewSet(viewsets.ModelViewSet): # GET : get_events
    queryset=Event.objects.all()
    def list(self,request,cafe_pk):
        cafe=Cafe.objects.get(pk=cafe_pk)
        queryset=Event.objects.filter(cafe=cafe)
        serializer=EventSerializer(queryset,many=True)
        return Response(serializer.data)

@csrf_exempt
def get_search_cafe(request):
    if request.method=="POST":
        locationX = float(request.POST['locationX'])
        locationY = float(request.POST['locationY'])
        all_cafe=Cafe.objects.all()
        cafes=[]
        for cafe in all_cafe:
            deltaX=cafe.locationX - locationX
            deltaY=cafe.locationY - locationY
            radius=math.sqrt(deltaX*deltaX+deltaY*deltaY)
            cafe_info={}
            if radius<5:
                cafe_info['locationString']=cafe.locationString
                cafe_info['name'] = cafe.name
                cafe_info['pk']=cafe.pk

                if cafe.cafe_image==None:
                    cafe_info['image_url'] = ''
                else :
                    cafe_info['image_url'] = cafe.cafe_image.url
                cafes.append(cafe_info)

        return HttpResponse(json.dumps(cafes), status=200)
    return HttpResponse(status=400)
