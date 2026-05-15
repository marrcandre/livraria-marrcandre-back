from django.db import transaction
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view, inline_serializer
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from core.models import Compra, User
from core.models.compra import ItensCompra
from core.serializers import (
    CompraAdicionarLivroAoCarrinhoSerializer,
    CompraCreateUpdateSerializer,
    CompraListSerializer,
    CompraSerializer,
)


@extend_schema_view(
    list=extend_schema(
        summary="Listar compras",
        description="Retorna a lista de compras. Administradores e gerentes vêem todas as compras; usuários comuns vêem apenas as próprias.",
        responses={200: CompraListSerializer(many=True)},
    ),
    retrieve=extend_schema(
        summary="Detalhar compra",
        description="Retorna os dados completos de uma compra específica.",
        responses={200: CompraSerializer},
    ),
    create=extend_schema(
        summary="Criar compra",
        description="Cria um novo carrinho de compras com os itens informados.",
        request=CompraCreateUpdateSerializer,
        responses={201: CompraCreateUpdateSerializer, 400: None},
    ),
    update=extend_schema(
        summary="Atualizar compra",
        description="Substitui todos os itens de uma compra existente.",
        request=CompraCreateUpdateSerializer,
        responses={200: CompraCreateUpdateSerializer, 400: None, 404: None},
    ),
    partial_update=extend_schema(
        summary="Atualizar compra parcialmente",
        description="Atualiza parcialmente os itens de uma compra existente.",
        request=CompraCreateUpdateSerializer,
        responses={200: CompraCreateUpdateSerializer, 400: None, 404: None},
    ),
    destroy=extend_schema(
        summary="Remover compra",
        description="Remove uma compra do sistema.",
        responses={204: None, 404: None},
    ),
)
class CompraViewSet(ModelViewSet):
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['usuario__email', 'status', 'data']
    search_fields = ['usuario__email']
    ordering_fields = ['usuario__email', 'status', 'data']
    ordering = ['-data']
    permission_classes = [IsAuthenticated]
    queryset = Compra.objects.order_by('-id')

    def get_queryset(self):
        usuario = self.request.user
        if usuario.is_superuser:
            return Compra.objects.prefetch_related('itens').prefetch_related('itens__livro').prefetch_related('usuario').order_by('-id')
        if usuario.groups.filter(name='administradores'):
            return Compra.objects.prefetch_related('itens').prefetch_related('itens__livro').prefetch_related('usuario').order_by('-id')
        if usuario.tipo_usuario == User.TipoUsuario.GERENTE:
            return Compra.objects.prefetch_related('itens').prefetch_related('itens__livro').prefetch_related('usuario').order_by('-id')
        return Compra.objects.filter(usuario=usuario).prefetch_related('itens').prefetch_related('itens__livro').prefetch_related('usuario').order_by('-id')

    def get_serializer_class(self):
        if self.action == 'list':
            return CompraListSerializer
        if self.action in {'create', 'update', 'partial_update'}:
            return CompraCreateUpdateSerializer
        return CompraSerializer

    @extend_schema(
        summary="Finalizar compra",
        description="Finaliza a compra do carrinho do usuário autenticado. Retorna 400 se a compra já foi finalizada ou se algum item ultrapassar o estoque disponível.",
        responses={
            200: inline_serializer('FinalizarOkResponse', fields={'status': serializers.CharField()}),
            400: inline_serializer('FinalizarErroResponse', fields={
                'status': serializers.CharField(),
                'livro': serializers.CharField(required=False),
                'quantidade_disponivel': serializers.IntegerField(required=False),
            }),
            404: None,
        },
    )
    @action(detail=True, methods=['post'])
    def finalizar(self, request, pk=None):
        ''' Finaliza a compra do carrinho de compras.'''
        compra = self.get_object()

        if compra.status != Compra.StatusCompra.CARRINHO:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={'status': 'Compra já finalizada'},
            )

        with transaction.atomic():
            for item in compra.itens.all():
                if item.quantidade > item.livro.quantidade:
                    return Response(
                        status=status.HTTP_400_BAD_REQUEST,
                        data={
                            'status': 'Quantidade insuficiente',
                            'livro': item.livro.titulo,
                            'quantidade_disponivel': item.livro.quantidade,
                        },
                    )

                item.livro.quantidade -= item.quantidade
                item.livro.save()

            compra.status = Compra.StatusCompra.FINALIZADO
            compra.save()

        return Response(status=status.HTTP_200_OK, data={'status': 'Compra finalizada'})

    @extend_schema(
        summary="Relatório de vendas do mês",
        description="Gera um relatório com o total de vendas e a quantidade de vendas do mês atual.",
        responses={200: inline_serializer(
            name='RelatorioVendasMesResponse',
            fields={
                'status': serializers.CharField(),
                'total_vendas': serializers.FloatField(),
                'quantidade_vendas': serializers.IntegerField(),
            },
        )},
    )
    @action(detail=False, methods=['get'])
    def relatorio_vendas_mes(self, request):
        agora = timezone.now()
        inicio_mes = agora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        compras = Compra.objects.filter(status=Compra.StatusCompra.FINALIZADO, data__gte=inicio_mes)

        total_vendas = sum(compra.total for compra in compras)
        quantidade_vendas = compras.count()

        return Response(
            {
                'status': 'Relatório de vendas deste mês',
                'total_vendas': total_vendas,
                'quantidade_vendas': quantidade_vendas,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Adicionar livro ao carrinho",
        description="Adiciona um livro ao carrinho de compras do usuário autenticado.",
        request=CompraAdicionarLivroAoCarrinhoSerializer,
        responses={200: CompraSerializer, 400: None, 404: None},
    )
    @action(detail=False, methods=['post'])
    def adicionar_ao_carrinho(self, request):
        serializer = CompraAdicionarLivroAoCarrinhoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        livro = serializer.validated_data['livro_id']
        quantidade = serializer.validated_data['quantidade']
        usuario = request.user

        if not usuario.is_authenticated:
            return Response(
                {'detail': 'Autenticação necessária.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        compra, criada = Compra.objects.get_or_create(
            usuario=usuario,
            status=Compra.StatusCompra.CARRINHO,
            defaults={'tipo_pagamento': Compra.TipoPagamento.CARTAO_CREDITO},
        )

        item_existente = compra.itens.filter(livro=livro).first()
        if item_existente:
            item_existente.quantidade += quantidade
            item_existente.save()
        else:
            ItensCompra.objects.create(
                compra=compra,
                livro=livro,
                quantidade=quantidade,
                preco=livro.preco,
            )

        compra_serializada = CompraSerializer(compra)

        return Response(
            compra_serializada.data,
            status=status.HTTP_200_OK if not criada else status.HTTP_201_CREATED,
        )
