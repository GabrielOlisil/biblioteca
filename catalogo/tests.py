from django.test import TestCase

from .models import Autor, Livro


class LivroDisponibilidadeTests(TestCase):
    def setUp(self):
        self.autor = Autor.objects.create(nome="Autor Teste")

    def test_bloqueio_manual_mantem_estoque_disponivel_na_regra_efetiva(self):
        livro = Livro.objects.create(
            titulo="Livro Bloqueado",
            autor=self.autor,
            genero="Teste",
            quantidade_exemplares=3,
            indisponivel_manual=True,
        )

        livro.refresh_from_db()

        self.assertFalse(livro.disponivel)
        self.assertEqual(livro.exemplares_disponiveis, 3)
