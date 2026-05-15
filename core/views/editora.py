from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.viewsets import ModelViewSet

from core.models import Editora
from core.serializers import EditoraSerializer


@extend_schema_view(
    list=extend_schema(
        summary="Listar editoras",
        description="Retorna a lista de editoras. Suporta busca por nome e cidade, e ordenação.",
    ),
    retrieve=extend_schema(
        summary="Detalhar editora",
        description="Retorna os dados de uma editora específica.",
    ),
    create=extend_schema(
        summary="Criar editora",
        description="Cadastra uma nova editora.",
    ),
    update=extend_schema(
        summary="Atualizar editora",
        description="Atualiza os dados de uma editora específica.",
    ),
    partial_update=extend_schema(
        summary="Atualizar editora parcialmente",
        description="Atualiza parcialmente os dados de uma editora específica.",
    ),
    destroy=extend_schema(
        summary="Remover editora",
        description="Remove uma editora do sistema.",
    ),
)

class EditoraViewSet(ModelViewSet):
    queryset = Editora.objects.order_by('-id')
    serializer_class = EditoraSerializer
    search_fields = ['nome', 'cidade']
    filter_backends = (SearchFilter, OrderingFilter)
