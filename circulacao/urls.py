from django.urls import path
from .views import (
    IndexView,
    UsuarioListView, UsuarioCreateView, UsuarioUpdateView,
    EmprestimoListView, EmprestimoCreateView, EmprestimoReturnView,
    ReservaListView, FazerReservaView,
    RelatorioAtrasadosPDFView
)

urlpatterns = [
    # Dashboard
    path("", IndexView.as_view(), name="index"),

    # Leitores (Bibliotecário)
    path("usuarios/", UsuarioListView.as_view(), name="usuario_list"),
    path("usuarios/novo/", UsuarioCreateView.as_view(), name="usuario_create"),
    path("usuarios/<int:pk>/editar/", UsuarioUpdateView.as_view(), name="usuario_update"),

    # Empréstimos (Bibliotecário)
    path("emprestimos/", EmprestimoListView.as_view(), name="emprestimo_list"),
    path("emprestimos/novo/", EmprestimoCreateView.as_view(), name="emprestimo_create"),
    path("emprestimos/<int:pk>/devolver/", EmprestimoReturnView.as_view(), name="emprestimo_return"),

    # Reservas (Leitor e Bibliotecário)
    path("reservas/", ReservaListView.as_view(), name="reserva_list"),
    path("livros/<int:pk>/reservar/", FazerReservaView.as_view(), name="fazer_reserva"),

    # PDF de Atrasados (Bibliotecário)
    path("relatorio/atrasados/", RelatorioAtrasadosPDFView.as_view(), name="relatorio_atrasados"),
]
