from django.contrib import admin

from .models import AlunoProfile, Aula, Matricula, Presenca, ProfessorProfile, QrCheckinToken, Turma

admin.site.register(ProfessorProfile)
admin.site.register(AlunoProfile)
admin.site.register(Turma)
admin.site.register(Matricula)
admin.site.register(Aula)
admin.site.register(Presenca)
admin.site.register(QrCheckinToken)
