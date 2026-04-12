from django.urls import path
from . import views

app_name = "chamada"

urlpatterns = [
    path("chamada/", views.chamada, name="chamada"),
    path("configuracao/", views.configuracao, name="configuracao"),
    path("qrcode/", views.qrcode, name="qrcode"),
    path("turmas/", views.turmas, name="turmas"),
    path("professor/", views.professor, name="professor"),
]
