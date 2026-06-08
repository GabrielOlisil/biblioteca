# Biblioteca

Projeto desenvolvido com Django, utilizando a arquitetura multi-app para maior organização e manutenção.

## Apps do Projeto
- **`catalogo`**: Responsável por gerenciar o acervo da biblioteca (Autores e Livros).
- **`circulacao`**: Responsável por gerenciar a interação com os usuários (Empréstimos, Reservas, Relatórios e Dashboard).

---

# Executando com Python

## Pré-requisitos

- Python instalado
- Pip instalado

## Instalação das dependências

```bash
pip install -r requirements.txt
```

## Banco de Dados e Dados Iniciais

Como a estrutura do banco foi remodelada, crie as tabelas e povoe a base com os dados iniciais de teste (admin/admin123 e leitor/leitor123):

```bash
python manage.py makemigrations catalogo circulacao
python manage.py migrate
python seed.py
```

## Executando o servidor

```bash
python manage.py runserver
```

O projeto estará disponível em:

```text
http://127.0.0.1:8000
```

---

# Executando com Docker

## Pré-requisitos

- Docker
- Docker Compose

## Executando o projeto

```bash
docker compose up -d
```

O projeto estará disponível em:

```text
http://localhost:8080
```

---

# Executando com UV

## Pré-requisitos

- UV instalado

## Instalando as dependências

```bash
uv sync
```

## Banco de Dados e Dados Iniciais

```bash
uv run python manage.py makemigrations catalogo circulacao
uv run python manage.py migrate
uv run python seed.py
```

## Executando o servidor

```bash
uv run python manage.py runserver
```

O projeto estará disponível em:

```text
http://127.0.0.1:8000
```