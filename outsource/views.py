from django.shortcuts import render
from outsource.models import *

from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets
from outsource.serializers import DeviceSerializer,JSONWebTokenSerializer
from rest_framework.response import Response
from rest_framework import status


@csrf_exempt
def payment(request):
    price=4000
    name="오레오 초코쉐이크"
    if request.method=="POST":
        if not request.POST.get('price')==None:
            price=request.POST.get('price')

        if not request.POST.get('name') == None:
            name = request.POST.get('name')

    return render(request,'payment.html', {'price':price, 'name':name})

def payment_complete(request):
    return render(request,'payment_complete.html')

class DeviceViewSet(viewsets.ModelViewSet):
    queryset = MyDevice.objects.all()
    serializer_class = DeviceSerializer

    def create(self, request):
        device=MyDevice.objects.filter(dev_id=request.data['dev_id'])
        if device.count()==0 :
            serializer = DeviceSerializer(data=request.data)
        else :
            device=device.first()
            serializer = DeviceSerializer(device, data=request.data)
            print(serializer)


        if serializer.is_valid():
            
            serializer.save(name=request.user.username, user_id=request.user.pk,is_active=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        print(serializer.errors)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST);

    def update(self,request):
        device = MyDevice.objects.filter(name=request.user.username)
        if device.count()==0:
            return Response(status=401)

        device=device.first()
        if request.data['is_active'] == 'true':
            device.is_active = True
        else :
            device.is_active = False

        device.save()

        return Response(status=200)

