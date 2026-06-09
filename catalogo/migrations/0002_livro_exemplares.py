from django.db import migrations, models


def ajustar_disponibilidade_existente(apps, schema_editor):
    Livro = apps.get_model('catalogo', 'Livro')
    Emprestimo = apps.get_model('circulacao', 'Emprestimo')
    Reserva = apps.get_model('circulacao', 'Reserva')

    for livro in Livro.objects.all():
        emprestimos_ativos = Emprestimo.objects.filter(livro_id=livro.id, data_devolucao_real__isnull=True).count()
        reservas_ativas = Reserva.objects.filter(livro_id=livro.id, ativa=True).count()
        ocupados = emprestimos_ativos + reservas_ativas

        livro.indisponivel_manual = not livro.disponivel and ocupados == 0
        livro.disponivel = livro.quantidade_exemplares > ocupados and not livro.indisponivel_manual
        livro.save(update_fields=['indisponivel_manual', 'disponivel'])


class Migration(migrations.Migration):

    dependencies = [
        ('catalogo', '0001_initial'),
        ('circulacao', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='livro',
            name='quantidade_exemplares',
            field=models.PositiveIntegerField(default=1, verbose_name='Quantidade de Exemplares'),
        ),
        migrations.AddField(
            model_name='livro',
            name='indisponivel_manual',
            field=models.BooleanField(default=False, verbose_name='Indisponível Manualmente'),
        ),
        migrations.RunPython(ajustar_disponibilidade_existente, migrations.RunPython.noop),
    ]