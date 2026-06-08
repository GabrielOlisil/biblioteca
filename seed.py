import os
import django
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'biblioteca.settings')
django.setup()

from catalogo.models import Autor, Livro
from circulacao.models import Emprestimo, Reserva
from django.contrib.auth.models import User

# 1. Criar Superusuário (Bibliotecário)
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print("Superusuário 'admin' criado com senha 'admin123'")

# 2. Criar Leitor
if not User.objects.filter(username='leitor').exists():
    leitor = User.objects.create_user('leitor', 'leitor@example.com', 'leitor123')
    leitor.first_name = "João"
    leitor.last_name = "Silva"
    leitor.save()
    print("Leitor 'leitor' criado com senha 'leitor123'")
else:
    leitor = User.objects.get(username='leitor')

# 3. Criar Autores
autores_dados = [
    {"nome": "J.R.R. Tolkien", "nacionalidade": "Britânico"},
    {"nome": "Machado de Assis", "nacionalidade": "Brasileiro"},
    {"nome": "George R.R. Martin", "nacionalidade": "Norte-americano"},
    {"nome": "Clarice Lispector", "nacionalidade": "Brasileira"}
]

autores = {}
for ad in autores_dados:
    autor, created = Autor.objects.get_or_create(nome=ad["nome"], defaults={"nacionalidade": ad["nacionalidade"]})
    autores[ad["nome"]] = autor
    if created:
        print(f"Autor '{autor.nome}' criado.")

# 4. Criar Livros
livros_dados = [
    {"titulo": "O Senhor dos Anéis", "autor": autores["J.R.R. Tolkien"], "genero": "Fantasia", "disponivel": True},
    {"titulo": "O Hobbit", "autor": autores["J.R.R. Tolkien"], "genero": "Fantasia", "disponivel": True},
    {"titulo": "Dom Casmurro", "autor": autores["Machado de Assis"], "genero": "Romance", "disponivel": True},
    {"titulo": "Memórias Póstumas de Brás Cubas", "autor": autores["Machado de Assis"], "genero": "Romance", "disponivel": True},
    {"titulo": "A Guerra dos Tronos", "autor": autores["George R.R. Martin"], "genero": "Fantasia", "disponivel": True},
    {"titulo": "A Hora da Estrela", "autor": autores["Clarice Lispector"], "genero": "Drama", "disponivel": True}
]

livros = {}
for ld in livros_dados:
    livro, created = Livro.objects.get_or_create(titulo=ld["titulo"], defaults={"autor": ld["autor"], "genero": ld["genero"], "disponivel": ld["disponivel"]})
    livros[ld["titulo"]] = livro
    if created:
        print(f"Livro '{livro.titulo}' criado.")

# 5. Criar Empréstimos (ativos, devolvidos e atrasados)
hoje = date.today()

# Empréstimo devolvido no prazo
emp1, created = Emprestimo.objects.get_or_create(
    livro=livros["O Hobbit"],
    usuario=leitor,
    defaults={
        "data_devolucao_prevista": hoje - timedelta(days=5),
        "data_devolucao_real": hoje - timedelta(days=6),
        "valor_multa": 0.00
    }
)
if created:
    livros["O Hobbit"].disponivel = True
    livros["O Hobbit"].save()
    print("Empréstimo (devolvido em dia) criado para O Hobbit.")

# Empréstimo devolvido com atraso
emp2, created = Emprestimo.objects.get_or_create(
    livro=livros["Dom Casmurro"],
    usuario=leitor,
    defaults={
        "data_devolucao_prevista": hoje - timedelta(days=10),
        "data_devolucao_real": hoje - timedelta(days=7),
        "valor_multa": 6.00
    }
)
if created:
    livros["Dom Casmurro"].disponivel = True
    livros["Dom Casmurro"].save()
    print("Empréstimo (devolvido com atraso) criado para Dom Casmurro.")

# Empréstimo ativo (livro ocupado)
emp3, created = Emprestimo.objects.get_or_create(
    livro=livros["O Senhor dos Anéis"],
    usuario=leitor,
    defaults={
        "data_devolucao_prevista": hoje + timedelta(days=5),
        "data_devolucao_real": None,
        "valor_multa": 0.00
    }
)
if created:
    livros["O Senhor dos Anéis"].disponivel = False
    livros["O Senhor dos Anéis"].save()
    print("Empréstimo ativo criado para O Senhor dos Anéis (livro indisponível).")

# Empréstimo em atraso (para aparecer no PDF!)
emp4, created = Emprestimo.objects.get_or_create(
    livro=livros["A Guerra dos Tronos"],
    usuario=leitor,
    defaults={
        "data_devolucao_prevista": hoje - timedelta(days=4),
        "data_devolucao_real": None,
        "valor_multa": 0.00
    }
)
if created:
    livros["A Guerra dos Tronos"].disponivel = False
    livros["A Guerra dos Tronos"].save()
    print("Empréstimo atrasado criado para A Guerra dos Tronos (livro indisponível).")

print("Banco de dados populado com sucesso!")
