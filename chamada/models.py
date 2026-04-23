from django.conf import settings
from django.db import models


class ProfessorProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="professor_profile"
    )
    nome_completo = models.CharField(max_length=200)
    registro_profissional = models.CharField(max_length=50, blank=True)

    def __str__(self) -> str:
        return self.nome_completo


class AlunoProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="aluno_profile"
    )
    nome_completo = models.CharField(max_length=200)
    matricula = models.CharField(max_length=50, unique=True)

    def __str__(self) -> str:
        return self.nome_completo


class Turma(models.Model):
    nome = models.CharField(max_length=120)
    codigo = models.CharField(max_length=30, unique=True)
    professor = models.ForeignKey(
        ProfessorProfile, on_delete=models.PROTECT, related_name="turmas"
    )

    def __str__(self) -> str:
        return f"{self.nome} ({self.codigo})"


class Matricula(models.Model):
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE, related_name="matriculas")
    aluno = models.ForeignKey(
        AlunoProfile, on_delete=models.CASCADE, related_name="matriculas"
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["turma", "aluno"], name="uniq_matricula_turma_aluno")
        ]


class Aula(models.Model):
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE, related_name="aulas")
    criada_por = models.ForeignKey(
        ProfessorProfile, on_delete=models.PROTECT, related_name="aulas_criadas"
    )
    inicio_em = models.DateTimeField()
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Aula {self.turma.codigo} @ {self.inicio_em:%Y-%m-%d %H:%M}"


class Presenca(models.Model):
    class Status(models.TextChoices):
        PRESENTE = "PRESENTE", "Presente"
        FALTA = "FALTA", "Falta"

    aula = models.ForeignKey(Aula, on_delete=models.CASCADE, related_name="presencas")
    aluno = models.ForeignKey(
        AlunoProfile, on_delete=models.CASCADE, related_name="presencas"
    )
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.FALTA)
    marcado_em = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["aula", "aluno"], name="uniq_presenca_aula_aluno")
        ]


class QrCheckinToken(models.Model):
    aula = models.ForeignKey(Aula, on_delete=models.CASCADE, related_name="qr_tokens")
    token = models.CharField(max_length=64, unique=True)
    expires_at = models.DateTimeField()
    created_by = models.ForeignKey(
        ProfessorProfile, on_delete=models.PROTECT, related_name="qr_tokens_criados"
    )
    criado_em = models.DateTimeField(auto_now_add=True)
