from datetime import timedelta

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.utils import timezone

from .models import (
    AlunoProfile,
    Aula,
    Matricula,
    Presenca,
    ProfessorProfile,
    QrCheckinToken,
    Turma,
)


class QrCheckinFlowTests(TestCase):
    def setUp(self):
        self.client = Client()

        self.prof_user = User.objects.create_user(username="prof", password="12345678")
        self.prof = ProfessorProfile.objects.create(user=self.prof_user, nome_completo="Prof")

        self.aluno_user = User.objects.create_user(username="aluno", password="12345678")
        self.aluno = AlunoProfile.objects.create(
            user=self.aluno_user, nome_completo="Aluno", matricula="M1"
        )

        self.turma = Turma.objects.create(nome="Turma 1", codigo="T1", professor=self.prof)
        Matricula.objects.create(turma=self.turma, aluno=self.aluno)

        self.aula = Aula.objects.create(
            turma=self.turma, criada_por=self.prof, inicio_em=timezone.now()
        )
        self.qr = QrCheckinToken.objects.create(
            aula=self.aula,
            token="tok1",
            created_by=self.prof,
            expires_at=timezone.now() + timedelta(seconds=60),
        )

    def test_qr_redirects_to_login_when_not_authenticated(self):
        resp = self.client.get(f"/chamada/qr/{self.qr.token}/")
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/login/", resp["Location"])
        self.assertIn("next=", resp["Location"])

    def test_qr_marks_presence_when_authenticated_student(self):
        self.client.login(username="aluno", password="12345678")
        resp = self.client.get(f"/chamada/qr/{self.qr.token}/")
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(
            Presenca.objects.filter(aula=self.aula, aluno=self.aluno, status=Presenca.Status.PRESENTE).exists()
        )

    def test_qr_expired_shows_invalid_page(self):
        self.client.login(username="aluno", password="12345678")
        self.qr.expires_at = timezone.now() - timedelta(seconds=1)
        self.qr.save(update_fields=["expires_at"])

        resp = self.client.get(f"/chamada/qr/{self.qr.token}/")
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "expirado", status_code=200)
