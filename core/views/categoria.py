from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.viewsets import ModelViewSet

from core.models import Categoria
from core.serializers import CategoriaSerializer


@extend_schema_view(
    list=extend_schema(
        summary="Listar categorias",
        description="Retorna a lista de categorias. Suporta busca por descrição e ordenação.",
    ),
    retrieve=extend_schema(
        summary="Detalhar categoria",
        description="Retorna os dados de uma categoria específica.",
    ),
    create=extend_schema(
        summary="Criar categoria",
        description="Cadastra uma nova categoria.",
    ),
    update=extend_schema(
        summary="Atualizar categoria",
        description="Atualiza os dados de uma categoria específica.",
    ),
    partial_update=extend_schema(
        summary="Atualizar categoria parcialmente",
        description="Atualiza parcialmente os dados de uma categoria específica.",
    ),
    destroy=extend_schema(
        summary="Remover categoria",
        description="Remove uma categoria do sistema.",
    ),
)

class CategoriaViewSet(ModelViewSet):
    queryset = Categoria.objects.order_by('-id')
    search_fields = ['descricao']
    filter_backends = (SearchFilter, OrderingFilter)
    serializer_class = CategoriaSerializer
