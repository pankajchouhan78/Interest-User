from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    SentRequestSerializer,
    AcceptInterestSerializer,
    UserSerializer,
)
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from django.db.models import Q
import requests
import base64
from interest_app.models import Interest, Interest_User


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {"message": "User created successfully"}, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data["username"]
            password = serializer.validated_data["password"]
            user = authenticate(username=username, password=password)
            if user is not None:
                credentials = f"{username}:{password}"
                encoded_credentials = base64.b64encode(credentials.encode()).decode()
                # print("encode credntials: ", encoded_credentials)
                headers = {
                    "message": "Login Successful",
                    "Authorization": f"Basic {encoded_credentials}",
                }
                # response = requests.get(
                #     'http://127.0.0.1:65533/User_interest/users/',
                #     headers=headers
                # )
                # print(response.status_code)
                # print(response.text)
                return Response(headers, status=status.HTTP_200_OK)
            return Response(
                {"message": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UsersList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = User.objects.exclude(username=request.user.username)
        serializer = UserSerializer(user, many=True)
        return Response({"data": serializer.data})


class SentRequestView(APIView):
    def post(self, request):
        serializer = SentRequestSerializer(data=request.data)
        if serializer.is_valid():
            sender_user = request.user
            try:
                receiver_user = User.objects.get(id=serializer.data.get("to_user"))
            except User.DoesNotExist:
                return Response(
                    {"msg": "User does not exists"}, status=status.HTTP_400_BAD_REQUEST
                )
            if Interest.objects.filter(
                Q(from_user=sender_user) and Q(to_user=receiver_user)
            ).exists():
                return Response(
                    {"msg": "Request already sent !!"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            Interest.objects.create(
                from_user=sender_user,
                to_user=receiver_user,
                message=serializer.data.get("message"),
            )
            return Response({"msg": "Request has been sent"}, status=status.HTTP_200_OK)
        return Response({"msg": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class AcceptInterestView(APIView):
    def post(self, request):
        receiver_user = request.user
        # import pdb; pdb.set_trace()
        serializer = AcceptInterestSerializer(data=request.data)
        if serializer.is_valid():
            try:
                sender_user = User.objects.get(id=serializer.data.get("to_user"))
            except Interest.DoesNotExist:
                return Response(
                    {"msg": "User does not exists"}, status=status.HTTP_400_BAD_REQUEST
                )
            if receiver_user.id == sender_user:
                return Response("User can't send Interest requst to itself !")
            try:
                interest_request = Interest.objects.get(
                    from_user=sender_user,
                    to_user=receiver_user,
                    accepted=False,
                    rejected=False,
                )
            except Interest.DoesNotExist:
                return Response(
                    {"msg": "Interest request does not exist or is already accepted"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            # Mark the request as accepted
            interest_request.accepted = True
            interest_request.save()
            # Create users list
            new_receiver_user = Interest_User.objects.create(user=receiver_user)
            new_receiver_user.interest_list.add(sender_user)
            new_receiver_user.save()
            new_sender_user = Interest_User.objects.create(user=sender_user)
            new_sender_user.interest_list.add(receiver_user)
            new_sender_user.save()
            return Response(
                {"msg": "Interest request accepted"}, status=status.HTTP_200_OK
            )
        return Response({"msg": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class RejectInterestView(APIView):
    def post(self, request):
        receiver_user = request.user
        # import pdb;pdb.set_trace()
        serializer = AcceptInterestSerializer(data=request.data)
        if serializer.is_valid():
            try:
                sender_user = User.objects.get(id=serializer.data.get("to_user"))
            except Interest.DoesNotExist:
                return Response(
                    {"msg": "User does not exists"}, status=status.HTTP_400_BAD_REQUEST
                )
            try:
                interest_request = Interest.objects.get(
                    from_user=sender_user,
                    to_user=receiver_user,
                    accepted=False,
                    rejected=False,
                )
            except Interest.DoesNotExist:
                return Response(
                    {"msg": "Interest request does not exist or is already rejected"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            # Mark the request as accepted
            interest_request.rejected = True
            interest_request.save()
            return Response(
                {"msg": "Interest request Rejected"}, status=status.HTTP_200_OK
            )
        return Response({"msg": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
