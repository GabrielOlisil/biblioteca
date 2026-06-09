from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, TemplateView
from django.urls import reverse_lazy
from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import FileResponse
from io import BytesIO
import json
from datetime import date
from django.db.models import Count

from .models import Emprestimo, Reserva
from catalogo.models import Autor, Livro

# ==========================================
# MIXIN DE ACESSO
# ==========================================

class BibliotecarioRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Garante que apenas bibliotecários (staff) acessem a view."""
    def test_func(self):
        return self.request.user.is_staff

# ==========================================
# FORMS CUSTOMIZADOS
# ==========================================

class UsuarioForm(forms.ModelForm):
    password = forms.CharField(label="Senha", widget=forms.PasswordInput(), required=False, help_text="Deixe em branco para manter a senha atual (ao editar)")

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user

class EmprestimoForm(forms.ModelForm):
    class Meta:
        model = Emprestimo
        fields = ['livro', 'usuario', 'data_devolucao_prevista']
        widgets = {
            'data_devolucao_prevista': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Permite selecionar apenas livros efetivamente disponíveis
        self.fields['livro'].queryset = Livro.objects.filter(disponivel=True).order_by('titulo')
        # Permite selecionar apenas leitores comuns (não staff)
        self.fields['usuario'].queryset = User.objects.filter(is_staff=False)

# ==========================================
# VIEWS: USUÁRIOS (Bibliotecário)
# ==========================================

class UsuarioListView(BibliotecarioRequiredMixin, ListView):
    model = User
    template_name = "circulacao/usuario_list.html"
    context_object_name = "usuarios"

    def get_queryset(self):
        return User.objects.filter(is_staff=False).order_by('username')

class UsuarioCreateView(BibliotecarioRequiredMixin, CreateView):
    model = User
    form_class = UsuarioForm
    template_name = "circulacao/usuario_form.html"
    success_url = reverse_lazy('usuario_list')

    def form_valid(self, form):
        messages.success(self.request, "Usuário Leitor cadastrado com sucesso!")
        return super().form_valid(form)

class UsuarioUpdateView(BibliotecarioRequiredMixin, UpdateView):
    model = User
    form_class = UsuarioForm
    template_name = "circulacao/usuario_form.html"
    success_url = reverse_lazy('usuario_list')

    def form_valid(self, form):
        messages.success(self.request, "Usuário Leitor atualizado com sucesso!")
        return super().form_valid(form)

# ==========================================
# VIEWS: EMPRÉSTIMOS E DEVOLUÇÕES (Bibliotecário)
# ==========================================

class EmprestimoListView(BibliotecarioRequiredMixin, ListView):
    model = Emprestimo
    template_name = "circulacao/emprestimo_list.html"
    context_object_name = "emprestimos"
    ordering = ['-data_emprestimo']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['today'] = date.today()
        return context

class EmprestimoCreateView(BibliotecarioRequiredMixin, CreateView):
    model = Emprestimo
    form_class = EmprestimoForm
    template_name = "circulacao/emprestimo_form.html"
    success_url = reverse_lazy('emprestimo_list')

    def form_valid(self, form):
        messages.success(self.request, "Empréstimo registrado com sucesso!")
        return super().form_valid(form)

class EmprestimoReturnView(BibliotecarioRequiredMixin, View):
    """View para processar a devolução e cálculo de multas."""
    def post(self, request, pk):
        emprestimo = get_object_or_404(Emprestimo, pk=pk)
        if not emprestimo.data_devolucao_real:
            emprestimo.devolver()
            if emprestimo.valor_multa > 0:
                messages.warning(
                    request, 
                    f"Livro '{emprestimo.livro.titulo}' devolvido com atraso. Multa gerada: R$ {emprestimo.valor_multa:.2f}"
                )
            else:
                messages.success(request, f"Livro '{emprestimo.livro.titulo}' devolvido com sucesso sem multas!")
        else:
            messages.info(request, "Este empréstimo já foi devolvido.")
        return redirect('emprestimo_list')

# ==========================================
# VIEWS: RESERVAS (Leitor e Bibliotecário)
# ==========================================

class ReservaListView(LoginRequiredMixin, ListView):
    model = Reserva
    template_name = "circulacao/reserva_list.html"
    context_object_name = "reservas"

    def get_queryset(self):
        if self.request.user.is_staff:
            return Reserva.objects.all().order_by('-data_reserva')
        return Reserva.objects.filter(usuario=self.request.user).order_by('-data_reserva')

class FazerReservaView(LoginRequiredMixin, View):
    """Permite que o Leitor realize a reserva de um livro disponível."""
    def post(self, request, pk):
        livro = get_object_or_404(Livro, pk=pk)
        if livro.disponivel:
            Reserva.objects.create(livro=livro, usuario=request.user, ativa=True)
            messages.success(request, f"Reserva do livro '{livro.titulo}' realizada com sucesso!")
        else:
            messages.error(request, "Este livro não está disponível para reserva.")
        return redirect('livro_list')

# ==========================================
# DASHBOARD E GRÁFICOS (Chart.js)
# ==========================================

class IndexView(LoginRequiredMixin, TemplateView):
    template_name = "circulacao/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Métricas gerais
        context['total_livros'] = Livro.objects.count()
        context['total_autores'] = Autor.objects.count()
        context['total_leitores'] = User.objects.filter(is_staff=False).count()
        context['emprestimos_ativos'] = Emprestimo.objects.filter(data_devolucao_real__isnull=True).count()
        
        # Filtra os gêneros mais procurados nos empréstimos do mês atual
        hoje = date.today()
        primeiro_dia_mes = date(hoje.year, hoje.month, 1)
        
        dados_genero = Emprestimo.objects.filter(
            data_emprestimo__gte=primeiro_dia_mes
        ).values('livro__genero').annotate(total=Count('id')).order_by('-total')
        
        # Formata dados para enviar em JSON para o Chart.js no front-end
        labels = [item['livro__genero'] for item in dados_genero]
        valores = [item['total'] for item in dados_genero]
        
        context['chart_labels'] = json.dumps(labels)
        context['chart_values'] = json.dumps(valores)
        
        # Para leitores: exibe alguns livros em destaque (disponíveis)
        context['livros_destaque'] = Livro.objects.filter(disponivel=True)[:6]
        
        return context

# ==========================================
# RELATÓRIO PDF (ReportLab)
# ==========================================

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter

class RelatorioAtrasadosPDFView(BibliotecarioRequiredMixin, View):
    """Gera um PDF com os empréstimos em atraso."""
    def get(self, request):
        atrasados = Emprestimo.objects.filter(
            data_devolucao_real__isnull=True,
            data_devolucao_prevista__lt=date.today()
        ).order_by('data_devolucao_prevista')

        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=letter,
            rightMargin=40, 
            leftMargin=40, 
            topMargin=40, 
            bottomMargin=40
        )
        
        story = []
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=22,
            textColor=colors.HexColor('#1e293b'),
            spaceAfter=15,
            alignment=1  # Center
        )
        
        header_style = ParagraphStyle(
            'HeaderStyle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=10,
            textColor=colors.white
        )
        
        cell_style = ParagraphStyle(
            'CellStyle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9,
            textColor=colors.HexColor('#334155')
        )
        
        story.append(Paragraph("Relatório de Livros Atrasados", title_style))
        story.append(Paragraph(f"Emitido em: {date.today().strftime('%d/%m/%Y')}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        if not atrasados.exists():
            story.append(Paragraph("Nenhum livro atrasado encontrado no sistema.", styles['Heading3']))
        else:
            data = [
                [
                    Paragraph("Livro", header_style),
                    Paragraph("Leitor", header_style),
                    Paragraph("Data Empréstimo", header_style),
                    Paragraph("Devolução Prevista", header_style),
                    Paragraph("Dias de Atraso", header_style),
                    Paragraph("Multa Acumulada", header_style)
                ]
            ]
            
            for emp in atrasados:
                dias_atraso = (date.today() - emp.data_devolucao_prevista).days
                multa = dias_atraso * 2.00
                data.append([
                    Paragraph(emp.livro.titulo, cell_style),
                    Paragraph(emp.usuario.username, cell_style),
                    Paragraph(emp.data_emprestimo.strftime('%d/%m/%Y'), cell_style),
                    Paragraph(emp.data_devolucao_prevista.strftime('%d/%m/%Y'), cell_style),
                    Paragraph(str(dias_atraso), cell_style),
                    Paragraph(f"R$ {multa:.2f}", cell_style)
                ])
            
            col_widths = [140, 80, 80, 85, 67, 80] # Total 532pt
            t = Table(data, colWidths=col_widths)
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f172a')),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('TOPPADDING', (0,0), (-1,0), 8),
                ('BOTTOMPADDING', (0,0), (-1,0), 8),
                ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.HexColor('#f8fafc'), colors.white]),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
                ('TOPPADDING', (0,1), (-1,-1), 6),
                ('BOTTOMPADDING', (0,1), (-1,-1), 6),
            ]))
            story.append(t)
            
        doc.build(story)
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename='relatorio_atrasados.pdf')
