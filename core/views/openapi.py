from drf_spectacular.utils import OpenApiResponse, OpenApiTypes


VALIDATION_ERROR = OpenApiResponse(
    response=OpenApiTypes.OBJECT,
    description='Objeto JSON com os erros de validação, organizados por campo.',
)
NOT_FOUND_ERROR = OpenApiResponse(
    response=OpenApiTypes.OBJECT,
    description='Objeto JSON informando que o recurso não foi encontrado.',
)
AUTHENTICATION_ERROR = OpenApiResponse(
    response=OpenApiTypes.OBJECT,
    description='Objeto JSON informando que a autenticação é necessária ou inválida.',
)
PERMISSION_ERROR = OpenApiResponse(
    response=OpenApiTypes.OBJECT,
    description='Objeto JSON informando que o usuário não tem permissão para a operação.',
)