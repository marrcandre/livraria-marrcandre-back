from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.viewsets import ModelViewSet

from core.models import Autor
from core.serializers import AutorSerializer


@extend_schema_view(
    list=extend_schema(
        summary="Listar autores",
        description="Retorna a lista de autores. Suporta busca por nome e ordenação.",
    ),
    retrieve=extend_schema(
        summary="Detalhar autor",
        description="Retorna os dados de um autor específico.",
    ),
    create=extend_schema(
        summary="Criar autor",
        description="Cadastra um novo autor.",
    ),
    update=extend_schema(
        summary="Atualizar autor",
        description="Atualiza os dados de um autor específico.",
    ),
    partial_update=extend_schema(
        summary="Atualizar autor parcialmente",
        description="Atualiza parcialmente os dados de um autor específico.",
    ),
    destroy=extend_schema(
        summary="Remover autor",
        description="Remove um autor do sistema.",
    ),
)

class AutorViewSet(ModelViewSet):
    queryset = Autor.objects.order_by('-id')
    serializer_class = AutorSerializer
    search_fields = ['nome']
    filter_backends = (SearchFilter, OrderingFilter)
