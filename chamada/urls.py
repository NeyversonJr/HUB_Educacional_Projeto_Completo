from django.urls import path
from . import views

app_name = "chamada"

urlpatterns = [
    path("chamada/", views.chamada, name="chamada"),
    path("turma/<int:turma_id>/aula/nova/", views.criar_aula, name="criar_aula"),
    path("aula/<int:aula_id>/", views.detalhe_aula, name="detalhe_aula"),
    path("configuracao/", views.configuracao, name="configuracao"),
    path("qrcode/", views.qrcode, name="qrcode"),
    path("turma/<int:turma_id>/qr/nova/", views.gerar_qr_nova_aula, name="gerar_qr_nova_aula"),
    path("qr/<str:token>/", views.qr_checkin, name="qr_checkin"),
    path("turmas/", views.turmas, name="turmas"),
    path("turmas/<int:turma_id>/remover/", views.remover_turma, name="remover_turma"),
    path("turmas/<int:turma_id>/editar/", views.editar_turma, name="editar_turma"),
    path("professor/", views.professor, name="professor"),
    path("cadastro/professor/", views.cadastro_professor, name="cadastro_professor"),
    path("cadastro/aluno/", views.cadastro_aluno, name="cadastro_aluno"),
]
