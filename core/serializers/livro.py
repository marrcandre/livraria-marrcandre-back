from rest_framework.serializers import (
    CharField,
    DecimalField,
    EmailField,
    FloatField,
    IntegerField,
    ModelSerializer,
    Serializer,
    SerializerMethodField,
    SlugRelatedField,
    ValidationError,
)
from drf_spectacular.utils import extend_schema_field, inline_serializer

from core.models import Livro
from uploader.models import Image
from uploader.serializers import ImageSerializer


class LivroAdicionarAoCarrinhoSerializer(Serializer):
    quantidade = IntegerField(default=1, min_value=1)

    def validate(self, data):
        livro = self.context.get('livro')
        if not livro:
            raise ValidationError('Livro não fornecido no contexto.')
        if data['quantidade'] > livro.quantidade:
            raise ValidationError('Quantidade solicitada não disponível em estoque.')
        return data


class LivroAjustarEstoqueSerializer(Serializer):
    quantidade = IntegerField()

    def validate_quantidade(self, value):
        livro = self.context.get('livro')
        if livro:
            nova_quantidade = livro.quantidade + value
            if nova_quantidade < 0:
                raise ValidationError('A quantidade em estoque não pode ser negativa.')
        return value


class LivroAlterarPrecoSerializer(Serializer):
    preco = DecimalField(max_digits=10, decimal_places=2)

    def validate_preco(self, value):
        """Valida se o preço é um valor positivo."""
        if value <= 0:
            raise ValidationError('O preço deve ser um valor positivo.')
        return value


class LivroComFavoritosSerializer(ModelSerializer):
    media_notas = SerializerMethodField()
    total_favoritos = SerializerMethodField()
    comentarios = SerializerMethodField()

    class Meta:
        model = Livro
        fields = ['id', 'titulo', 'media_notas', 'total_favoritos', 'comentarios']

    @extend_schema_field(FloatField())
    def get_media_notas(self, obj):
        notas = obj.favoritos.exclude(nota__isnull=True).values_list('nota', flat=True)
        if not notas:
            return 0
        return sum(notas) / len(notas)

    @extend_schema_field(IntegerField())
    def get_total_favoritos(self, obj):
        return obj.favoritos.count()

    @extend_schema_field(
        inline_serializer(
            name='ComentarioFavorito',
            fields={
                'usuario__email': EmailField(),
                'comentario': CharField(),
                'nota': IntegerField(allow_null=True, required=False),
            },
            many=True,
        )
    )
    def get_comentarios(self, obj):
        return obj.favoritos.exclude(comentario__isnull=True).values('usuario__email', 'comentario', 'nota')


class LivroListSerializer(ModelSerializer):
    capa = ImageSerializer(required=False)

    class Meta:
        model = Livro
        fields = ['id', 'titulo', 'preco', 'isbn', 'quantidade', 'categoria', 'editora', 'autores', 'capa']
        depth = 1


class LivroMaisVendidoSerializer(ModelSerializer):
    total_vendidos = IntegerField()

    class Meta:
        model = Livro
        fields = ['id', 'titulo', 'total_vendidos']


class LivroRetrieveSerializer(ModelSerializer):
    capa = ImageSerializer(required=False)

    class Meta:
        model = Livro
        fields = '__all__'
        depth = 1


class LivroSerializer(ModelSerializer):
    capa_attachment_key = SlugRelatedField(
        source='capa',
        queryset=Image.objects.all(),
        slug_field='attachment_key',
        required=False,
        write_only=True,
    )
    capa = ImageSerializer(required=False, read_only=True)

    class Meta:
        model = Livro
        fields = '__all__'
