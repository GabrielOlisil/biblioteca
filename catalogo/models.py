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
    quantidade_exemplares = models.PositiveIntegerField(default=1, verbose_name="Quantidade de Exemplares")
    indisponivel_manual = models.BooleanField(default=False, verbose_name="Indisponível Manualmente")
    disponivel = models.BooleanField(default=True, verbose_name="Disponível")

    @property
    def exemplares_ocupados(self):
        return self.emprestimos.filter(data_devolucao_real__isnull=True).count() + self.reservas.filter(ativa=True).count()

    @property
    def exemplares_disponiveis(self):
        return max(self.quantidade_exemplares - self.exemplares_ocupados, 0)

    def recalcular_disponibilidade(self):
        nova_disponibilidade = self.exemplares_disponiveis > 0 and not self.indisponivel_manual
        if self.disponivel != nova_disponibilidade:
            self.disponivel = nova_disponibilidade
            models.Model.save(self, update_fields=["disponivel"])
        return self.disponivel

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.recalcular_disponibilidade()

    def __str__(self):
        return self.titulo
