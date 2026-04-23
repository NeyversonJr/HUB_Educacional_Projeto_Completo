from django.urls import path
from . import views

app_name = "educadigital"

urlpatterns = [
    path("", views.home, name="home"),
    path("cursos/", views.cursos, name="cursos"),
    path("cadastro/", views.cadastro, name="cadastro"),

    path("matematica/", views.matematica, name="matematica"),
    path("matematica/6/", views.matematica6, name="matematica6"),
    path("matematica/7/", views.matematica7, name="matematica7"),
    path("matematica/8/", views.matematica8, name="matematica8"),
    path("matematica/9/", views.matematica9, name="matematica9"),

    path("portugues/", views.portugues, name="portugues"),
    path("portugues/6/", views.portugues6, name="portugues6"),
    path("portugues/7/", views.portugues7, name="portugues7"),
    path("portugues/8/", views.portugues8, name="portugues8"),
    path("portugues/9/", views.portugues9, name="portugues9"),

    path("historia/", views.historia, name="historia"),
    path("historia/6/", views.historia6, name="historia6"),
    path("historia/7/", views.historia7, name="historia7"),
    path("historia/8/", views.historia8, name="historia8"),
    path("historia/9/", views.historia9, name="historia9"),

    path("geografia/", views.geografia, name="geografia"),
    path("geografia/6/", views.geografia6, name="geografia6"),
    path("geografia/7/", views.geografia7, name="geografia7"),
    path("geografia/8/", views.geografia8, name="geografia8"),
    path("geografia/9/", views.geografia9, name="geografia9"),

    path("api/get-quiz/", views.get_quiz, name="get_quiz"),
]
