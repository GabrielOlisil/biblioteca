from datetime import date, timedelta

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase

from catalogo.models import Autor, Livro

from .models import Emprestimo, Reserva


class CirculacaoExemplaresTests(TestCase):
    def setUp(self):
        self.autor = Autor.objects.create(nome="Autor Teste")
        self.usuario = User.objects.create_user(username="leitor", password="123456")
        self.outro_usuario = User.objects.create_user(username="leitor2", password="123456")

    def test_emprestimos_consumem_exemplares_ate_esgotar(self):
        livro = Livro.objects.create(
            titulo="Livro com 2 Exemplares",
            autor=self.autor,
            genero="Teste",
            quantidade_exemplares=2,
        )

        Emprestimo.objects.create(
            livro=livro,
            usuario=self.usuario,
            data_devolucao_prevista=date.today() + timedelta(days=7),
        )
        livro.refresh_from_db()
        self.assertTrue(livro.disponivel)
        self.assertEqual(livro.exemplares_disponiveis, 1)

        Emprestimo.objects.create(
            livro=livro,
            usuario=self.outro_usuario,
            data_devolucao_prevista=date.today() + timedelta(days=7),
        )
        livro.refresh_from_db()
        self.assertFalse(livro.disponivel)
        self.assertEqual(livro.exemplares_disponiveis, 0)

    def test_devolucao_libera_exemplar(self):
        livro = Livro.objects.create(
            titulo="Livro Devolvido",
            autor=self.autor,
            genero="Teste",
            quantidade_exemplares=1,
        )

        emprestimo = Emprestimo.objects.create(
            livro=livro,
            usuario=self.usuario,
            data_devolucao_prevista=date.today() + timedelta(days=7),
        )
        livro.refresh_from_db()
        self.assertFalse(livro.disponivel)

        emprestimo.devolver()

        livro.refresh_from_db()
        self.assertTrue(livro.disponivel)
        self.assertEqual(livro.exemplares_disponiveis, 1)

    def test_bloqueio_manual_impede_emprestimo_mesmo_com_exemplares(self):
        livro = Livro.objects.create(
            titulo="Livro Bloqueado",
            autor=self.autor,
            genero="Teste",
            quantidade_exemplares=2,
            indisponivel_manual=True,
        )

        with self.assertRaises(ValidationError):
            Emprestimo.objects.create(
                livro=livro,
                usuario=self.usuario,
                data_devolucao_prevista=date.today() + timedelta(days=7),
            )

    def test_reserva_consumida_ate_esgotar(self):
        livro = Livro.objects.create(
            titulo="Livro Reservável",
            autor=self.autor,
            genero="Teste",
            quantidade_exemplares=2,
        )

        Reserva.objects.create(livro=livro, usuario=self.usuario)
        livro.refresh_from_db()
        self.assertTrue(livro.disponivel)
        self.assertEqual(livro.exemplares_disponiveis, 1)

        Reserva.objects.create(livro=livro, usuario=self.outro_usuario)
        livro.refresh_from_db()
        self.assertFalse(livro.disponivel)
        self.assertEqual(livro.exemplares_disponiveis, 0)
