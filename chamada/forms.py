from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Turma, AlunoProfile


class CadastroProfessorForm(UserCreationForm):
    nome_completo = forms.CharField(max_length=200)
    email = forms.EmailField(required=False)
    registro_profissional = forms.CharField(max_length=50, required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "nome_completo", "registro_profissional")


class CadastroAlunoForm(UserCreationForm):
    nome_completo = forms.CharField(max_length=200)
    email = forms.EmailField(required=False)
    matricula = forms.CharField(max_length=50)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "nome_completo", "matricula")


class TurmaForm(forms.ModelForm):
    alunos = forms.ModelMultipleChoiceField(
        queryset=AlunoProfile.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'mt-1 w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-200'}),
        required=False,
        help_text="Selecione os alunos para matricular nesta turma."
    )

    class Meta:
        model = Turma
        fields = ("nome", "codigo")


class TurmaNomeForm(forms.ModelForm):
    class Meta:
        model = Turma
        fields = ("nome",)


class TurmaEditForm(forms.ModelForm):
    alunos = forms.ModelMultipleChoiceField(
        queryset=AlunoProfile.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'mt-1 w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-200'}),
        required=False,
        help_text="Selecione os alunos matriculados nesta turma."
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            self.fields['alunos'].initial = self.instance.matriculas.values_list('aluno', flat=True)

    class Meta:
        model = Turma
        fields = ("nome",)

