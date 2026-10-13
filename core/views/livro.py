from django.db.models.aggregates import Sum
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
    extend_schema,
    extend_schema_view,
    inline_serializer,
)
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from core.models import Compra, Favorito, ItensCompra, Livro
from core.serializers import (
    CompraSerializer,
    FavoritoSerializer,
    LivroAdicionarAoCarrinhoSerializer,
    LivroAjustarEstoqueSerializer,
    LivroAlterarPrecoSerializer,
    LivroListSerializer,
    LivroMaisVendidoSerializer,
    LivroRetrieveSerializer,
    LivroSerializer,
)
from core.views.openapi import AUTHENTICATION_ERROR, NOT_FOUND_ERROR, PERMISSION_ERROR, VALIDATION_ERROR


@extend_schema_view(
    list=extend_schema(
        summary='Listar livros',
        description=(
            'Retorna livros paginados, ordenados por título por padrão. '
            'Permite filtrar por categoria (categoria__descricao) e editora (editora__nome) '
            'com correspondência exata, e por quantidade e preço com valores exatos '
            'ou limites mínimo (__gte) e máximo (__lte). '
            'O parâmetro search busca no título; ordering aceita titulo ou preco, '
            'com o prefixo "-" para ordem decrescente. '
            'A paginação aceita page e page_size, com 10 itens por padrão e máximo de 100.'
        ),
        responses={200: LivroListSerializer(many=True)},
    ),
    retrieve=extend_schema(
        summary='Detalhar livro',
        description='Retorna os dados completos de um livro específico.',
        responses={200: LivroRetrieveSerializer},
    ),
    create=extend_schema(
        summary='Criar livro',
        description='Cadastra um novo livro.',
        request=LivroSerializer,
        responses={201: LivroSerializer, 400: None},
    ),
    update=extend_schema(
        summary='Atualizar livro',
        description='Atualiza todos os dados de um livro específico.',
        request=LivroSerializer,
        responses={200: LivroSerializer, 400: None, 404: None},
    ),
    partial_update=extend_schema(
        summary='Atualizar livro parcialmente',
        description='Atualiza parcialmente os dados de um livro específico.',
        request=LivroSerializer,
        responses={200: LivroSerializer, 400: None, 404: None},
    ),
    destroy=extend_schema(
        summary='Remover livro',
        description='Remove um livro do sistema.',
        responses={204: None, 404: None},
    ),
)
class LivroViewSet(ModelViewSet):
    queryset = Livro.objects.order_by('-id')
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = {
        'categoria__descricao': ['exact'],
        'editora__nome': ['exact'],
        'quantidade': ['exact', 'gte', 'lte'],
        'preco': ['exact', 'gte', 'lte'],
    }
    search_fields = ['titulo']
    ordering_fields = ['titulo', 'preco']
    ordering = ['titulo']

    def get_serializer_class(self):
        if self.action == 'list':
            return LivroListSerializer
        elif self.action == 'retrieve':
            return LivroRetrieveSerializer

        return LivroSerializer

    @extend_schema(
        summary='Alterar preço do livro',
        description='Permite alterar o preço de um livro específico.',
        request=LivroAlterarPrecoSerializer,
        responses={
            200: inline_serializer('AlterarPrecoResponse', fields={'detail': serializers.CharField()}),
            400: VALIDATION_ERROR,
            401: AUTHENTICATION_ERROR,
            403: PERMISSION_ERROR,
            404: NOT_FOUND_ERROR,
        },
    )
    @action(detail=True, methods=['patch'])
    def alterar_preco(self, request, pk=None):
        livro = self.get_object()

        serializer = LivroAlterarPrecoSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        livro.preco = serializer.validated_data['preco']
        livro.save()

        return Response(
            {'detail': f"Preço do livro '{livro.titulo}' atualizado para {livro.preco}."}, status=status.HTTP_200_OK
        )

    @extend_schema(
        summary='Ajustar estoque do livro',
        description='Permite ajustar a quantidade em estoque de um livro específico.',
        request=LivroAjustarEstoqueSerializer,
        responses={
            200: inline_serializer(
                'AjustarEstoqueResponse',
                fields={
                    'status': serializers.CharField(),
                    'novo_estoque': serializers.IntegerField(),
                },
            ),
            400: VALIDATION_ERROR,
            401: AUTHENTICATION_ERROR,
            403: PERMISSION_ERROR,
            404: NOT_FOUND_ERROR,
        },
    )
    @action(detail=True, methods=['post'])
    def ajustar_estoque(self, request, pk=None):
        livro = self.get_object()

        serializer = LivroAjustarEstoqueSerializer(data=request.data, context={'livro': livro})
        serializer.is_valid(raise_exception=True)

        quantidade_ajuste = serializer.validated_data['quantidade']

        livro.quantidade += quantidade_ajuste
        livro.save()

        return Response(
            {'status': 'Quantidade ajustada com sucesso', 'novo_estoque': livro.quantidade}, status=status.HTTP_200_OK
        )

    @extend_schema(
        summary='Lista os livros mais vendidos',
        description='Retorna livros com mais de 10 itens associados a compras, sem filtrar o status da compra. Retorna uma lista vazia quando nenhum livro ultrapassa esse limite.',
        responses={
            200: OpenApiResponse(
                response=LivroMaisVendidoSerializer(many=True),
                examples=[OpenApiExample('Nenhum livro acima do limite', value=[], response_only=True)],
            ),
        },
    )
    @action(detail=False, methods=['get'])
    def mais_vendidos(self, request):
        livros = (
            Livro.objects
            .annotate(total_vendidos=Sum('itens_compra__quantidade'))
            .filter(total_vendidos__gt=10)
            .order_by('-total_vendidos')
        )

        serializer = LivroMaisVendidoSerializer(livros, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary='Adicionar livro ao carrinho',
        description='Adiciona um livro ao carrinho de compras do usuário autenticado.',
        request=LivroAdicionarAoCarrinhoSerializer,
        responses={
            200: CompraSerializer,
            400: VALIDATION_ERROR,
            401: AUTHENTICATION_ERROR,
            403: PERMISSION_ERROR,
            404: NOT_FOUND_ERROR,
        },
    )
    @action(detail=True, methods=['post'])
    def adicionar_ao_carrinho(self, request, pk=None):
        livro = self.get_object()

        serializer = LivroAdicionarAoCarrinhoSerializer(data=request.data, context={'livro': livro})
        serializer.is_valid(raise_exception=True)
        quantidade = serializer.validated_data['quantidade']

        compra, created = Compra.objects.get_or_create(usuario=request.user, status=Compra.StatusCompra.CARRINHO)

        item_existente = compra.itens.filter(livro=livro).first()

        if item_existente:
            item_existente.quantidade += quantidade
            item_existente.preco = livro.preco
            item_existente.save()
        else:
            ItensCompra.objects.create(compra=compra, livro=livro, quantidade=quantidade, preco=livro.preco)

        compra_serializada = CompraSerializer(compra)
        return Response(compra_serializada.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary='Favoritar livro',
        description='Cria um favorito ou atualiza um favorito existente. Se já existir, atualiza nota e/ou comentário.',
        request=FavoritoSerializer,
        responses={
            200: FavoritoSerializer,
            201: FavoritoSerializer,
            400: VALIDATION_ERROR,
            401: AUTHENTICATION_ERROR,
            403: PERMISSION_ERROR,
            404: NOT_FOUND_ERROR,
        },
        methods=['POST'],
    )
    @extend_schema(
        summary='Atualizar favorito',
        description='Atualiza nota e/ou comentário de um favorito existente. Retorna 404 se o livro ainda não estiver favoritado.',
        request=FavoritoSerializer,
        responses={
            200: FavoritoSerializer,
            400: VALIDATION_ERROR,
            401: AUTHENTICATION_ERROR,
            403: PERMISSION_ERROR,
            404: NOT_FOUND_ERROR,
        },
        methods=['PUT', 'PATCH'],
    )
    @action(detail=True, methods=['post', 'put', 'patch'])
    def favoritar(self, request, pk=None):
        """
        Favorita um livro ou atualiza os dados (nota e/ou comentário) de um favorito existente.
        """
        livro = self.get_object()
        favorito = Favorito.objects.filter(usuario=request.user, livro=livro).first()

        if not favorito and request.method in {'PUT', 'PATCH'}:
            return Response({'error': 'Livro não está na sua lista de favoritos'}, status=status.HTTP_404_NOT_FOUND)

        if favorito:
            # Atualiza favorito existente
            serializer = FavoritoSerializer(
                favorito, data=request.data, partial=True, context={'livro': livro, 'usuario': request.user}
            )
        else:
            # Cria novo favorito
            serializer = FavoritoSerializer(data=request.data, context={'livro': livro, 'usuario': request.user})

        serializer.is_valid(raise_exception=True)
        serializer.save()

        status_code = status.HTTP_200_OK if favorito else status.HTTP_201_CREATED
        return Response(serializer.data, status=status_code)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='search',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Pesquisa livros pelo título.',
            ),
            OpenApiParameter(
                name='ordering',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description=(
                    'Campo de ordenação: titulo ou preco. '
                    'Prefixe com "-" para ordem decrescente; '
                    'por exemplo, -preco.'
                ),
            ),
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
