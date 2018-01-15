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
from rest_framework_jwt.views import JSONWebTokenAPIView
from rest_framework.views import APIView
import facebook
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
            user=serializer.save()
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

    def destroy(self,request):
        request.user.delete()
        return Response(status=200)


class CafeBeverageList(viewsets.ModelViewSet):
    queryset=Beverage.objects.all()
    serializer_class = BeverageSerializer

    def retrieve(self, request,cafe_pk): # GET : get_cafe_beverage
        cafe=Cafe.objects.get(pk=cafe_pk)
        queryset=cafe.beverages.all()
        serializer = BeverageSerializer(queryset, many=True)
        return Response(serializer.data)

    def list(self, request): #  GET : get_cafes
        queryset=Cafe.objects.all()
        serializers=CafeSerializer(queryset,many=True)
        return Response(serializers.data)


class BeverageOption(APIView):
    def get(self, request,pk):
        beverage=Beverage.objects.get(pk=pk)
        serializers=BeverageOptionSerializer(beverage.options.all(),many=True)
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

class ReadyPayment(APIView):
    def post(self,request,cafe_pk):
        first_name=""
        count_beverage=0
        options = request.data.get('options')
        cafe=Cafe.objects.get(pk=cafe_pk)
        last_order = Order.objects.filter(cafe=cafe)
        order_num=get_orderNum(last_order)
        cafe.the_pay_order_num += 1
        cafe.save()
        amount_price = 0
        for option_info in options:
            for i in range(0, int(option_info['amount'])):
                beverage=Beverage.objects.get(pk=option_info['beverage'])
                cafe_pk=beverage.cafe.pk
                size_price = beverage.price.split()
                price = size_price[option_info['size']]
                price = int(price.split(':')[1])
                amount_price += price
                count_beverage+=1

                if first_name=="":
                    first_name=beverage.name

        order_num=str(cafe_pk)+"_"+datetime.datetime.now().strftime("%Y%m%d")+"_"+str(order_num)+"_"+str(cafe.the_pay_order_num)
        now_time = datetime.date.today()
        close_time = datetime.date(now_time.year, now_time.month, now_time.day+1).strftime("%Y-%m-%d")
        response={"order_num": order_num, "amount_price" : amount_price, "user_name":request.user.username, "cafe_name":cafe.name,
                  "user_phonenumber" : request.user.phone_number, "cafe_phonenumber": cafe.phone_number, "pay_closetime":close_time}
        if count_beverage>1 :
            response['menu_name']=first_name+" 및 "+ str(count_beverage-1)+"잔"
        else :
            response['menu_name'] = first_name
        return Response(response, status=200)


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    def create(self,request,cafe_pk): #  POST : order_beverage
        import time
        start_time = time.time()
        user = User.objects.get(pk=request.user.pk)
        cafe=Cafe.objects.get(pk=cafe_pk)
        serializer=OrderSerializer(data=request.data)

        last_order = Order.objects.filter(cafe=cafe)

        order_num = get_orderNum(last_order)


        if serializer.is_valid():
            order=serializer.save(orderer_id=request.user.pk,cafe_id=cafe_pk,order_num=order_num,get_time=request.data.get('get_time'))
            cafe.the_pay_order_num = 0
            cafe.save()

            options = request.data.get('options')

            amount_price=0
            for option_info in options:
                for i in range(0,int(option_info['amount'])):
                    option=BeverageOrderOption.objects.create(beverage_id=option_info['beverage'],
                                                         size=option_info['size'],
                                                         shot_num=option_info['shot_num'])

                    for option_selection in option_info['selections']:
                        optionSelction=OptionSelection.objects.get(id=option_selection)
                        amount_price+=optionSelction.add_price
                        option.options.add(option_selection)

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
                if order.options.count() > 1:
                    cafeDevice.send_message({'message': '[' + order.order_time.strftime('%Y-%m-%d') + '] ' +
                                                        order.options.first().beverage.name + " 및 " + str(order.options.count() - 1) + "잔" + '이 주문되었습니다!'},
                                                collapse_key="음료가 주문되었습니다!")
                elif order.options.count() == 1:
                        cafeDevice.send_message({
                                                    'message': '[' + order.order_time.strftime('%Y-%m-%d') + '] ' + order.options.first().beverage.name + '(이)가 주문되었습니다!'}
                                                , collapse_key="음료가 주문되었습니다!")

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

    def list(self, request,term_year,term_month): # GET : recent_payment_list_by_id
        user=User.objects.get(pk=request.user.pk)
        now_time = datetime.date.today()
        year=(now_time.year-int(term_year))*12+(now_time.month-int(term_month)-1)
        now_time = datetime.date(year//12, year%12+1, now_time.day)


        queryset = Order.objects.filter(orderer=user, order_time__gte=now_time).order_by('-order_time')
        serializer = OrderSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self,request,coupon_pk): # GET : recent_payment_list_by_order
        coupon = Coupon.objects.get(pk=coupon_pk)
        queryset = Order.objects.filter(orderer=coupon.user, cafe=coupon.cafe, is_done=True).order_by('-order_time')
        serializer = OrderSerializer(queryset, many=True)
        return Response(serializer.data)

def get_orderNum(last_order):
    if last_order.count() == 0:
        order_num = 0
    else:
        last_order = last_order.order_by('-order_time').first()
        last_order_date = last_order.order_time.date()
        now_order_date = timezone.now().today().date()
        if last_order_date == now_order_date:
            order_num = last_order.order_num + 1
        else:
            order_num = 0

    return order_num

class EventViewSet(viewsets.ModelViewSet): # GET : get_events
    queryset=Event.objects.all()
    def list(self,request):
        now_time=datetime.date.today()
        queryset=Event.objects.filter(from_time__gte=now_time)
        serializer=EventSerializer(queryset,many=True)
        return Response(serializer.data)

    def retrieve(self, request, cafe_pk):
        cafe = Cafe.objects.get(pk=cafe_pk)
        queryset = Event.objects.filter(cafe=cafe)
        serializer = EventSerializer(queryset, many=True)
        return Response(serializer.data)

class AlertViewSet(viewsets.ModelViewSet):
    quertset=Alert.objects.all()
    def list(self,request):
        now_time = datetime.date.today()
        queryset=Alert.objects.filter(alert_life__gte=now_time)
        serializer=AlertSerializer(queryset,many=True)
        return Response(serializer.data)

class SocialSignUp(viewsets.ModelViewSet):
    def create(self,request):
        token = request.data['access_token']
        graph = facebook.GraphAPI(token)
        profile = graph.get_object("me")
        facebook_uid = profile.get('id')

        data=request.data.copy()

        data['username'] = facebook_uid
        data['password'] = facebook_uid

        serializer = UserManageSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save()
            social = SocialUser(user=user, token=data['access_token'])
            social.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EmailCheck(APIView):
    def post(self, request):
        user = User.objects.filter(username=request.data['email'])
        if user.count()>=1:
            return Response(status=400)

        return Response(status=200)

class ObtainJSONWebToken(JSONWebTokenAPIView):
    serializer_class = JSONWebTokenSerializer
    def post(self,request,*args,**kwargs):
        token=request.data['access_token']
        graph = facebook.GraphAPI(token)
        profile = graph.get_object("me")
        facebook_uid=profile.get('id')

        user = User.objects.filter(username=facebook_uid)
        if user.count()==0:
            data = {}
            data['token'] = ""
            return Response(data, status=201)

        socialUser=SocialUser.objects.filter(user=user).first()

        if not request.data['access_token'] == socialUser.token:
            data={}
            data['token']=""
            return Response(data, status=status.HTTP_400_BAD_REQUEST)

        socialUser.token=request.data['access_token']
        socialUser.save()
        token=super(ObtainJSONWebToken, self).post(request, *args, **kwargs)

        return token



'''
class FacebookLoginViewSet(viewsets.ModelViewSet):
    queryset = MyDevice.objects.all()

    def create(self, request):
        graph = facebook.GraphAPI(
            access_token="EAARZAcWIH3J8BAMgzBzIARc4oaZAVu5QjaKZAy9L91ABwZCQLLcjE5ME8XZB0eM61MwR8gLcTlr6eKrrt6oy31bIp4NoURwrZAvVI1AfnABTJsZAlGQgvKooJNK62snCd5NmRAtKiZBHdplOcIO7UbAIw2XQqk5Q48Hk28hZABouEoMhSj34l3lsCjtwnnnJzpIHArJk4pVUDE5fpLrmSfnfe")

        args = {'fields': 'id,email,gender,birthday', }
        profile = graph.get_object('1076016075834444', **args)
        if profile['gender']=='male':
            profile['gender']=True
        else :
            profile['gender'] = False

        serializer = UserManageSerializer(data=profile)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=200)
    
    
    
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
'''