from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods
import base64
import io
import secrets
from datetime import timedelta

import qrcode as qr_module

from .forms import CadastroAlunoForm, CadastroProfessorForm, TurmaEditForm, TurmaForm
from .models import (
    AlunoProfile,
    Aula,
    Matricula,
    Presenca,
    ProfessorProfile,
    QrCheckinToken,
    Turma,
)


def _get_professor(request):
    if not request.user.is_authenticated:
        return None
    return getattr(request.user, "professor_profile", None)


def _get_aluno(request):
    if not request.user.is_authenticated:
        return None
    return getattr(request.user, "aluno_profile", None)


@login_required
def chamada(request):
    professor = _get_professor(request)
    if not professor:
        return HttpResponseForbidden("Acesso restrito ao professor.")

    turmas = Turma.objects.filter(professor=professor).order_by("nome")
    return render(request, "chamada/chamada.html", {"turmas": turmas})


def configuracao(request):
    return render(request, "chamada/configuração.html")


def qrcode(request):
    return render(request, "chamada/qrcode.html")


@login_required
@require_http_methods(["GET", "POST"])
def turmas(request):
    professor = _get_professor(request)
    if not professor:
        return HttpResponseForbidden("Acesso restrito ao professor.")

    if request.method == "POST":
        form = TurmaForm(request.POST)
        if form.is_valid():
            turma = form.save(commit=False)
            turma.professor = professor
            turma.save()
            alunos = form.cleaned_data.get('alunos', [])
            for aluno in alunos:
                Matricula.objects.get_or_create(turma=turma, aluno=aluno)
            return redirect("chamada:turmas")
    else:
        form = TurmaForm()

    turmas_qs = Turma.objects.filter(professor=professor).order_by("nome")
    return render(request, "chamada/turmas.html", {"turmas": turmas_qs, "form": form})


@login_required
@require_http_methods(["POST"])
def remover_turma(request, turma_id: int):
    professor = _get_professor(request)
    if not professor:
        return HttpResponseForbidden("Acesso restrito ao professor.")

    turma = get_object_or_404(Turma, id=turma_id, professor=professor)
    turma.delete()
    return redirect("chamada:turmas")


@login_required
@require_http_methods(["GET", "POST"])
def editar_turma(request, turma_id: int):
    professor = _get_professor(request)
    if not professor:
        return HttpResponseForbidden("Acesso restrito ao professor.")

    turma = get_object_or_404(Turma, id=turma_id, professor=professor)

    if request.method == "POST":
        form = TurmaEditForm(request.POST, instance=turma)
        if form.is_valid():
            form.save(update_fields=["nome"])
            alunos_selecionados = set(form.cleaned_data.get('alunos', []))
            matriculas_atuais = set(turma.matriculas.values_list('aluno', flat=True))
            # Remove matriculas não selecionadas
            for aluno_id in matriculas_atuais - alunos_selecionados:
                Matricula.objects.filter(turma=turma, aluno_id=aluno_id).delete()
            # Add novas matriculas
            for aluno in alunos_selecionados - matriculas_atuais:
                Matricula.objects.get_or_create(turma=turma, aluno=aluno)
            return redirect("chamada:turmas")
    else:
        form = TurmaEditForm(instance=turma)

    return render(request, "chamada/turma_edit.html", {"turma": turma, "form": form})


@login_required
def professor(request):
    professor = _get_professor(request)
    if not professor:
        return HttpResponseForbidden("Acesso restrito ao professor.")
    turmas = Turma.objects.filter(professor=professor).order_by("nome")
    return render(request, "chamada/professor.html", {"professor": professor, "turmas": turmas})


@login_required
def qrcode(request):
    professor = _get_professor(request)
    if not professor:
        return HttpResponseForbidden("Acesso restrito ao professor.")

    turmas = Turma.objects.filter(professor=professor).order_by("nome")
    return render(request, "chamada/qrcode.html", {"turmas": turmas})


@login_required
@require_http_methods(["POST"])
def gerar_qr_nova_aula(request, turma_id: int):
    professor = _get_professor(request)
    if not professor:
        return HttpResponseForbidden("Acesso restrito ao professor.")

    turma = get_object_or_404(Turma, id=turma_id, professor=professor)
    aula = Aula.objects.create(turma=turma, criada_por=professor, inicio_em=timezone.now())

    token_str = secrets.token_urlsafe(32)[:64]
    token = QrCheckinToken.objects.create(
        aula=aula,
        token=token_str,
        created_by=professor,
        expires_at=timezone.now() + timedelta(seconds=60),
    )

    checkin_url = request.build_absolute_uri(
        redirect("chamada:qr_checkin", token=token.token).url
    )

    qr = qr_module.QRCode(box_size=8, border=2)
    qr.add_data(checkin_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    qr_b64 = base64.b64encode(buf.getvalue()).decode("ascii")

    turmas = Turma.objects.filter(professor=professor).order_by("nome")
    return render(
        request,
        "chamada/qrcode.html",
        {"turmas": turmas, "aula": aula, "checkin_url": checkin_url, "qr_b64": qr_b64},
    )


@require_http_methods(["GET"])
def qr_checkin(request, token: str):
    if not request.user.is_authenticated:
        return redirect_to_login(request.get_full_path())

    aluno = _get_aluno(request)
    if not aluno:
        return HttpResponseForbidden("Acesso restrito ao aluno.")

    qr_token = get_object_or_404(
        QrCheckinToken.objects.select_related("aula", "aula__turma"), token=token
    )
    if qr_token.expires_at <= timezone.now():
        return render(request, "chamada/qr_invalid.html", {"motivo": "QR Code expirado."})

    # aluno precisa estar matriculado na turma
    if not Matricula.objects.filter(turma=qr_token.aula.turma, aluno=aluno).exists():
        return HttpResponseForbidden("Você não está matriculado nesta turma.")

    presenca, _created = Presenca.objects.get_or_create(
        aula=qr_token.aula, aluno=aluno, defaults={"status": Presenca.Status.PRESENTE}
    )
    if presenca.status != Presenca.Status.PRESENTE:
        presenca.status = Presenca.Status.PRESENTE
        presenca.save(update_fields=["status", "marcado_em"])

    return render(request, "chamada/qr_success.html", {"aula": qr_token.aula})


@login_required
@require_http_methods(["POST"])
def criar_aula(request, turma_id: int):
    professor = _get_professor(request)
    if not professor:
        return HttpResponseForbidden("Acesso restrito ao professor.")

    turma = get_object_or_404(Turma, id=turma_id, professor=professor)
    aula = Aula.objects.create(turma=turma, criada_por=professor, inicio_em=timezone.now())

    matriculas = Matricula.objects.filter(turma=turma).select_related("aluno")
    Presenca.objects.bulk_create(
        [Presenca(aula=aula, aluno=m.aluno, status=Presenca.Status.FALTA) for m in matriculas],
        ignore_conflicts=True,
    )

    return redirect("chamada:detalhe_aula", aula_id=aula.id)


@login_required
@require_http_methods(["GET", "POST"])
def detalhe_aula(request, aula_id: int):
    professor = _get_professor(request)
    if not professor:
        return HttpResponseForbidden("Acesso restrito ao professor.")

    aula = get_object_or_404(Aula.objects.select_related("turma", "criada_por"), id=aula_id)
    if aula.turma.professor_id != professor.id:
        return HttpResponseForbidden("Você não tem permissão para acessar esta aula.")

    if request.method == "POST":
        for key, value in request.POST.items():
            if not key.startswith("presenca_"):
                continue
            presenca_id = key.removeprefix("presenca_")
            if value not in (Presenca.Status.PRESENTE, Presenca.Status.FALTA):
                continue
            Presenca.objects.filter(id=presenca_id, aula=aula).update(status=value)
        return redirect("chamada:detalhe_aula", aula_id=aula.id)

    presencas = (
        Presenca.objects.filter(aula=aula)
        .select_related("aluno", "aluno__user")
        .order_by("aluno__nome_completo")
    )
    return render(request, "chamada/aula_detail.html", {"aula": aula, "presencas": presencas})


def cadastro_professor(request):
    if request.method == "POST":
        form = CadastroProfessorForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            if form.cleaned_data.get("email"):
                user.email = form.cleaned_data["email"]
            user.save()
            ProfessorProfile.objects.create(
                user=user,
                nome_completo=form.cleaned_data["nome_completo"],
                registro_profissional=form.cleaned_data.get("registro_profissional", ""),
            )
            login(request, user)
            messages.success(request, "Cadastro de professor realizado com sucesso!")
            return redirect("chamada:professor")
    else:
        form = CadastroProfessorForm()

    return render(request, "chamada/cadastro_professor.html", {"form": form})


def cadastro_aluno(request):
    if request.method == "POST":
        form = CadastroAlunoForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            if form.cleaned_data.get("email"):
                user.email = form.cleaned_data["email"]
            user.save()
            AlunoProfile.objects.create(
                user=user,
                nome_completo=form.cleaned_data["nome_completo"],
                matricula=form.cleaned_data["matricula"],
            )
            login(request, user)
            messages.success(request, "Cadastro de aluno realizado com sucesso!")
            return redirect("Site:index")
    else:
        form = CadastroAlunoForm()

    return render(request, "chamada/cadastro_aluno.html", {"form": form})
