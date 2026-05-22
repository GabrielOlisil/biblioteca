# Biblioteca

Projeto desenvolvido com Django.

---

# Executando com Python

## Pré-requisitos

- Python instalado
- Pip instalado

## Instalação das dependências

```bash
pip install -r requirements.txt
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

## Executando o servidor

```bash
uv run python manage.py runserver
```

O projeto estará disponível em:

```text
http://127.0.0.1:8000
```