from django.urls import path
from .views import (
    AutorListView, AutorCreateView, AutorUpdateView,
    LivroListView, LivroCreateView, LivroUpdateView,
    LivroDisponibilidadeAPIView
)

urlpatterns = [
    # Autores
    path("autores/", AutorListView.as_view(), name="autor_list"),
    path("autores/novo/", AutorCreateView.as_view(), name="autor_create"),
    path("autores/<int:pk>/editar/", AutorUpdateView.as_view(), name="autor_update"),

    # Livros
    path("livros/", LivroListView.as_view(), name="livro_list"),
    path("livros/novo/", LivroCreateView.as_view(), name="livro_create"),
    path("livros/<int:pk>/editar/", LivroUpdateView.as_view(), name="livro_update"),

    # API REST
    path("api/livros/", LivroDisponibilidadeAPIView.as_view(), name="api_livros"),
]
