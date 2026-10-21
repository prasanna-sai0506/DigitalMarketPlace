from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView, get_object_or_404
from rest_framework.viewsets import ModelViewSet
from .models import User, Profile
from .serializers import UserSerializer, ProfileSerializer, RegisterSerializer,LoginSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from digitalmarketplace.permissions import IsAdminOrOwner

class UserLoginAPIView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer
    def post(self,request):
        serializer = LoginSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']    
        password = serializer.validated_data['password']
                
        if not username or not password :
            return Response({"detail":"Username and Password are required"}, status = status.HTTP_400_BAD_REQUEST)      
        try:
            user = User.objects.get(username = username)
        except User.DoesNotExist:
            return Response({"detail":"Invalid Username or Password, Provide valid credentials  "})
        
        if not user.check_password(password):
            return Response({"detail":"invalid username or password!"}, status = status.HTTP_401_UNAUTHORIZED)
        
        if not user.is_active:
            return Response({"detail":"user is inactive"},status=status.HTTP_403_FORBIDDEN)

        refresh_token = RefreshToken.for_user(user)
        
        return Response({"refresh": str(refresh_token),"access":str(refresh_token.access_token)})
        
        
class RegistrationAPIView(APIView):
    permission_classes = [AllowAny]
    
    def post(self,request):
        serializer = RegisterSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data, status = status.HTTP_201_CREATED)
    

class CurrentUserAPIView(APIView):   # for checking the current user
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data,status = status.HTTP_200_OK)
        
    def patch(self,request):
        serializer = UserSerializer(request.user, data = request.data, partial = True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data,status=status.HTTP_200_OK,)


class CurrentProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_profile(self, user):
        profile, created = Profile.objects.get_or_create(user=user)
        return profile

    def get(self, request):
        serializer = ProfileSerializer(self.get_profile(request.user))
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        profile = self.get_profile(request.user)
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserProfileAPIView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        profile, created = Profile.objects.get_or_create(user=user)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class UserListCreateAPIView(APIView):  # allowing administrator to view all users 
    permission_classes = [IsAdminUser]
    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    

class UserDetailAPIView(APIView):    # allowing administrator to manage single user
    permission_classes = [IsAdminOrOwner]
    
    def get_object(self,pk):
        return get_object_or_404(User, pk = pk)
    
    def get(self,request,pk):
        user = self.get_object(pk)
        serializer = UserSerializer(user)
        return Response(serializer.data,status = status.HTTP_200_OK)
    
    def put(self,request,pk):
        user = self.get_object(pk)
        serializer = UserSerializer(user, data = request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status = status.HTTP_200_OK)
    
    def patch(self,request,pk):
        user = self.get_object(pk)
        serializer = UserSerializer(user, data = request.data,partial = True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def delete(self,request,pk):
        user = self.get_object(pk)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)