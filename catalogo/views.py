from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions

from .models import Autor, Livro
from .serializers import LivroSerializer

# ==========================================
# MIXIN DE ACESSO
# ==========================================

class BibliotecarioRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Garante que apenas bibliotecários (staff) acessem a view."""
    def test_func(self):
        return self.request.user.is_staff

# ==========================================
# VIEWS: AUTORES (Bibliotecário)
# ==========================================

class AutorListView(BibliotecarioRequiredMixin, ListView):
    model = Autor
    template_name = "catalogo/autor_list.html"
    context_object_name = "autores"
    paginate_by = 10

class AutorCreateView(BibliotecarioRequiredMixin, CreateView):
    model = Autor
    fields = ['nome', 'nacionalidade']
    template_name = "catalogo/autor_form.html"
    success_url = reverse_lazy('autor_list')

    def form_valid(self, form):
        messages.success(self.request, "Autor cadastrado com sucesso!")
        return super().form_valid(form)

class AutorUpdateView(BibliotecarioRequiredMixin, UpdateView):
    model = Autor
    fields = ['nome', 'nacionalidade']
    template_name = "catalogo/autor_form.html"
    success_url = reverse_lazy('autor_list')

    def form_valid(self, form):
        messages.success(self.request, "Autor atualizado com sucesso!")
        return super().form_valid(form)

# ==========================================
# VIEWS: LIVROS (Leitor e Bibliotecário)
# ==========================================

class LivroListView(LoginRequiredMixin, ListView):
    model = Livro
    template_name = "catalogo/livro_list.html"
    context_object_name = "livros"
    paginate_by = 12

    def get_queryset(self):
        queryset = super().get_queryset()
        busca = self.request.GET.get('busca')
        if busca:
            queryset = queryset.filter(titulo__icontains=busca)
        return queryset.order_by('titulo')

class LivroCreateView(BibliotecarioRequiredMixin, CreateView):
    model = Livro
    fields = ['titulo', 'autor', 'genero', 'disponivel']
    template_name = "catalogo/livro_form.html"
    success_url = reverse_lazy('livro_list')

    def form_valid(self, form):
        messages.success(self.request, "Livro cadastrado com sucesso!")
        return super().form_valid(form)

class LivroUpdateView(BibliotecarioRequiredMixin, UpdateView):
    model = Livro
    fields = ['titulo', 'autor', 'genero', 'disponivel']
    template_name = "catalogo/livro_form.html"
    success_url = reverse_lazy('livro_list')

    def form_valid(self, form):
        messages.success(self.request, "Livro atualizado com sucesso!")
        return super().form_valid(form)

# ==========================================
# API ENDPOINT (DRF)
# ==========================================

class LivroDisponibilidadeAPIView(APIView):
    """Endpoint aberto para consultar a disponibilidade de títulos em tempo real."""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        livros = Livro.objects.all().order_by('titulo')
        
        # Filtro de disponibilidade
        disponivel = request.query_params.get('disponivel')
        if disponivel is not None:
            is_disp = disponivel.lower() in ['true', '1']
            livros = livros.filter(disponivel=is_disp)
        
        # Filtro por título
        titulo = request.query_params.get('titulo')
        if titulo is not None:
            livros = livros.filter(titulo__icontains=titulo)
            
        serializer = LivroSerializer(livros, many=True)
        return Response(serializer.data)
