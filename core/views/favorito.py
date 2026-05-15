from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from core.models import Favorito, Livro
from core.serializers.favorito import (
    FavoritoDetailSerializer,
    FavoritoSerializer,
)
from core.serializers.livro import LivroComFavoritosSerializer


@extend_schema_view(
    list=extend_schema(
        summary="Listar favoritos",
        description="Retorna a lista de livros favoritados pelo usuário autenticado.",
        responses={200: FavoritoDetailSerializer(many=True)},
    ),
    retrieve=extend_schema(
        summary="Detalhar favorito",
        description="Retorna os dados de um favorito específico do usuário autenticado.",
        responses={200: FavoritoSerializer},
    ),
    create=extend_schema(
        summary="Adicionar favorito",
        description="Adiciona um livro à lista de favoritos do usuário autenticado.",
        request=FavoritoSerializer,
        responses={201: FavoritoSerializer, 400: None},
    ),
    update=extend_schema(
        summary="Atualizar favorito",
        description="Atualiza os dados (nota e/ou comentário) de um favorito específico.",
        request=FavoritoSerializer,
        responses={200: FavoritoSerializer, 400: None, 404: None},
    ),
    partial_update=extend_schema(
        summary="Atualizar favorito parcialmente",
        description="Atualiza parcialmente os dados de um favorito específico.",
        request=FavoritoSerializer,
        responses={200: FavoritoSerializer, 400: None, 404: None},
    ),
    destroy=extend_schema(
        summary="Remover favorito",
        description="Remove um livro da lista de favoritos do usuário autenticado.",
        responses={204: None, 404: None},
    ),
)
class FavoritoViewSet(ModelViewSet):
    queryset = Favorito.objects.all()
    serializer_class = FavoritoSerializer

    def get_queryset(self):
        # Filtra favoritos apenas do usuário logado
        return self.queryset.filter(usuario=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list':
            return FavoritoDetailSerializer
        return FavoritoSerializer

    def perform_create(self, serializer):
        # Automaticamente define o usuário como o usuário logado
        serializer.save(usuario=self.request.user)

    @extend_schema(
        summary="Livros com estatísticas de favoritos",
        description="Retorna os livros que possuem ao menos um favorito, com média de notas, total de favoritos e lista de comentários.",
        responses={200: LivroComFavoritosSerializer(many=True)},
    )
    @action(detail=False, methods=['get'])
    def livros_com_estatisticas(self, request):
        # Retorna apenas os livros que têm favoritos
        livros = Livro.objects.filter(favoritos__isnull=False).distinct()
        serializer = LivroComFavoritosSerializer(livros, many=True)
        return Response(serializer.data)
