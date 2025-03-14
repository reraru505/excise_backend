from django.shortcuts import render

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import SalesmanBarman
from .serializers import SalesmanBarmanSerializer

class SalesmanBarmanView (APIView ):

    def post (self , request ):


        serializer = SalesmanBarmanSerializer(data = request.data )

        if serializer.is_valid():
            serializer.save()
            return  Response(serializer.data, status=status.HTTP_201_CREATED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def get (self , request ):

        salesman_barman = SalesmanBarman.objects.all()
        serializer = SalesmanBarmanSerializer(salesman_barman , many=True)
        return Response(serializer.data)



