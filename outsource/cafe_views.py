from outsource.models import Cafe,Order,Coupon,Beverage,User,Event,Alert
from outsource.serializers import OrderSerializer,EventSerializer,AlertSerializer,CafeSerializerForCafe
from rest_framework.views import APIView
import datetime
from rest_framework.response import Response
from rest_framework import viewsets
from fcm.utils import get_device_model
from rest_framework import status
from django.http import QueryDict

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    def list(self, request):  # GET : get_orders
        cafe = Cafe.objects.get(pk=request.user.pk)
        queryset = cafe.orders.filter(is_done=False).order_by('-order_time')
        serializer = OrderSerializer(queryset, many=True)
        return Response(serializer.data)

    def update(self,request,pk): # POST :  complete_order
        order = Order.objects.get(pk=pk)

        Device = get_device_model()
        cafeDevice = Device.objects.filter(user=order.orderer)
        if not cafeDevice.count() == 0:
            cafeDevice = cafeDevice.first()
            if order.options.count() > 1:
                cafeDevice.send_message({'message': '[' + request.user.name + '] 주문하신 ' + order.options.first().beverage.name + " 및 " + str(
                    order.options.count() - 1) + "잔" + '이 준비되었습니다!'}, collapse_key="주문하신 음료가 준비되었습니다!")
            elif order.options.count() == 1:
                    cafeDevice.send_message({'message': '[' + request.user.name + '] 주문하신 ' + order.options.first().beverage.name + '(이)가 준비되었습니다!'}
                                            ,collapse_key="주문하신 음료가 준비되었습니다!")

        order.is_done = True
        order.save()
        serializer=OrderSerializer(order)
        return Response(serializer.data)

    def destroy(self, request,pk): # DELETE :  delete_order
        order = Order.objects.get(pk=pk)
        order.delete()
        return Response(status=200)

class BroadCastAdvertise(APIView):
    def get(self, request, beverage_pk): # GET : broadcast_advertise/beverage_pk
        beverage=Beverage.objects.get(pk=beverage_pk)
        cafe = Cafe.objects.get(pk=request.user.pk)
        users=User.objects.filter(favorite_cafe__pk=cafe.pk)

        if users.count()==0:
            return Response(status=400)
        for user in users:
            device=user.device.all()
            device.send_message({'message': cafe.name+'의 새로운 메뉴'+beverage.name+"(이)가 출시 되었습니다!"}, collapse_key="새 음료가 추가되었습니다!")

        return Response(status=200)

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    def list(self,request): # GET : get_my_events
        cafe=Cafe.objects.get(pk=request.user.pk)
        queryset=Event.objects.filter(cafe=cafe)
        serializer = EventSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self,request) : # POST : create_event
        serializer = EventSerializer(data=request.data)
        if serializer.is_valid():
            event=serializer.save(cafe_id=request.user.pk)
            beverages_pk = request.POST.getlist('beverages')
            for beverage_pk in beverages_pk:
                beverage = Beverage.objects.get(pk=beverage_pk)
                event.beverages.add(beverage)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CafeOpenUpdate(APIView):
    def post(self,request):
        cafe = Cafe.objects.get(pk=request.user.pk)
        cafe.is_open=request.data['is_open']
        cafe.save()
        return Response(status=200)

class OrderSetMaking(APIView):
    def post(self,request,pk):
        order = Order.objects.get(pk=pk)

        Device = get_device_model()
        cafeDevice = Device.objects.filter(user=order.orderer)
        if not cafeDevice.count() == 0:
            cafeDevice = cafeDevice.first()
            if order.options.count() > 1:
                cafeDevice.send_message(
                    {'message': '[' + request.user.name + '] 주문하신 ' + order.options.first().beverage.name + " 및 " + str(
                        order.options.count() - 1) + "잔" + '이 제조중입니다!'}, collapse_key="주문하신 음료가 제조중입니다!")
            elif order.options.count() == 1:
                cafeDevice.send_message({
                                            'message': '[' + request.user.name + '] 주문하신 ' + order.options.first().beverage.name + '(이)가 제조중입니다!'}
                                        , collapse_key="주문하신 음료가 제조중입니다!")

        order.is_making = True
        order.save()
        serializer = OrderSerializer(order)
        return Response(serializer.data)

class OrderSetEnd(APIView):
    def post(self, request, pk):
        order=Order.objects.get(pk=pk)
        order.is_end=True
        order.save()
        serializer = OrderSerializer(order)
        return Response(serializer.data)

class CafeMinTimeSet(APIView):
    def post(self, request):
        cafe = Cafe.objects.get(pk=request.user.pk)
        cafe.min_time=request.data['min_time']
        cafe.save()
        return Response(status=200)

class AlertViewSet(viewsets.ModelViewSet):
    queryset = Alert.objects.all()
    def create(self,request):
        serializer=AlertSerializer(data=request.data)
        if serializer.is_valid():
            alert=serializer.save(cafe_id=request.user.pk)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CafeViewSet(viewsets.ModelViewSet):
    queryset = Cafe.objects.all()
    def list(self, request): # GET : user-manage
        user = Cafe.objects.get(pk=request.user.pk)
        serializers=CafeSerializerForCafe(user)
        return Response(serializers.data)