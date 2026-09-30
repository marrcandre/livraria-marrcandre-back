from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from core.models import User
from core.serializers import UserRegistrationSerializer, UserSerializer
from core.views.openapi import AUTHENTICATION_ERROR, VALIDATION_ERROR


class UserViewSet(ModelViewSet):
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer

    @extend_schema(
        summary='Consultar usuário autenticado',
        description='Retorna os dados do usuário autenticado.',
        request=None,
        responses={200: UserSerializer, 401: AUTHENTICATION_ERROR},
        methods=['GET'],
    )
    @extend_schema(
        summary='Atualizar usuário autenticado',
        description='Atualiza parcialmente os dados do usuário autenticado.',
        request=UserSerializer,
        responses={
            200: UserSerializer,
            400: VALIDATION_ERROR,
            401: AUTHENTICATION_ERROR,
        },
        methods=['PATCH'],
    )
    @action(detail=False, methods=['get', 'patch'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Retorna ou atualiza os dados do usuário autenticado."""
        user = request.user
        if request.method == 'PATCH':
            serializer = UserSerializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    summary='Registro de novo usuário',
    description='Cria um novo usuário no sistema. Não requer autenticação.',
    request=UserRegistrationSerializer,
    responses={201: UserRegistrationSerializer, 400: None},
)
class UserRegistrationView(CreateAPIView):
    """Endpoint para registro de novos usuários."""

    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
