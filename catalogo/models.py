from django.db import models

class Autor(models.Model):
    nome = models.CharField(max_length=150, verbose_name="Nome")
    nacionalidade = models.CharField(max_length=100, verbose_name="Nacionalidade", blank=True, null=True)

    class Meta:
        verbose_name_plural = "Autores"

    def __str__(self):
        return self.nome

class Livro(models.Model):
    titulo = models.CharField(max_length=200, verbose_name="Título")
    autor = models.ForeignKey(Autor, on_delete=models.CASCADE, related_name="livros", verbose_name="Autor")
    genero = models.CharField(max_length=100, verbose_name="Gênero")
    disponivel = models.BooleanField(default=True, verbose_name="Disponível")

    def __str__(self):
        return self.titulo
