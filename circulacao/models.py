from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import date

class Emprestimo(models.Model):
    livro = models.ForeignKey('catalogo.Livro', on_delete=models.CASCADE, related_name="emprestimos", verbose_name="Livro")
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="emprestimos", verbose_name="Leitor")
    data_emprestimo = models.DateField(auto_now_add=True, verbose_name="Data de Empréstimo")
    data_devolucao_prevista = models.DateField(verbose_name="Data de Devolução Prevista")
    data_devolucao_real = models.DateField(null=True, blank=True, verbose_name="Data de Devolução Real")
    valor_multa = models.DecimalField(max_digits=6, decimal_places=2, default=0.00, verbose_name="Valor da Multa")

    def devolver(self):
        """Calcula a multa (R$ 2.00 por dia de atraso) e marca o livro como disponível."""
        self.data_devolucao_real = date.today()
        if self.data_devolucao_real > self.data_devolucao_prevista:
            dias_atraso = (self.data_devolucao_real - self.data_devolucao_prevista).days
            self.valor_multa = dias_atraso * 2.00
        else:
            self.valor_multa = 0.00
        self.save()

        self.livro.recalcular_disponibilidade()

    def delete(self, *args, **kwargs):
        livro = self.livro
        super().delete(*args, **kwargs)
        livro.recalcular_disponibilidade()

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        if is_new and (not self.livro.disponivel or self.livro.exemplares_disponiveis <= 0):
            raise ValidationError("Este livro não possui exemplares disponíveis para empréstimo.")
        super().save(*args, **kwargs)
        self.livro.recalcular_disponibilidade()

    def __str__(self):
        return f"Empréstimo de {self.livro} para {self.usuario.username}"

class Reserva(models.Model):
    livro = models.ForeignKey('catalogo.Livro', on_delete=models.CASCADE, related_name="reservas", verbose_name="Livro")
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reservas", verbose_name="Leitor")
    data_reserva = models.DateField(auto_now_add=True, verbose_name="Data de Reserva")
    ativa = models.BooleanField(default=True, verbose_name="Ativa")

    def delete(self, *args, **kwargs):
        livro = self.livro
        super().delete(*args, **kwargs)
        livro.recalcular_disponibilidade()

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        if is_new and self.ativa and (not self.livro.disponivel or self.livro.exemplares_disponiveis <= 0):
            raise ValidationError("Este livro não possui exemplares disponíveis para reserva.")
        super().save(*args, **kwargs)
        self.livro.recalcular_disponibilidade()

    def __str__(self):
        return f"Reserva de {self.livro} por {self.usuario.username}"
