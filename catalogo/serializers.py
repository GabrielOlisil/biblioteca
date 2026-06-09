from rest_framework import serializers
from .models import Livro, Autor

class AutorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Autor
        fields = ['id', 'nome', 'nacionalidade']

class LivroSerializer(serializers.ModelSerializer):
    autor = AutorSerializer(read_only=True)
    autor_id = serializers.PrimaryKeyRelatedField(
        queryset=Autor.objects.all(), source='autor', write_only=True
    )
    exemplares_disponiveis = serializers.IntegerField(read_only=True)

    class Meta:
        model = Livro
        fields = ['id', 'titulo', 'autor', 'autor_id', 'genero', 'quantidade_exemplares', 'exemplares_disponiveis', 'indisponivel_manual', 'disponivel']
