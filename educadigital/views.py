from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from .models import Category, Question
import random
import traceback


def home(request):
    return render(request, "educadigital/index.html")


def cursos(request):
    return render(request, "educadigital/cursos.html")


def cadastro(request):
    return render(request, "educadigital/cadastro.html")


def matematica(request):
    return render(request, "educadigital/matematica.html")


def matematica6(request):
    category = request.GET.get("category", "Matemática")
    context = {
        "category": category,
        "categories": Category.objects.all()
    }
    return render(request, "educadigital/matematica/6matematica.html", context)


def matematica7(request):
    return render(request, "educadigital/matematica/7matematica.html")


def matematica8(request):
    return render(request, "educadigital/matematica/8matematica.html")


def matematica9(request):
    return render(request, "educadigital/matematica/9matematica.html")


def portugues(request):
    return render(request, "educadigital/portugues.html")


def portugues6(request):
    return render(request, "educadigital/portugues/6portugues.html")


def portugues7(request):
    return render(request, "educadigital/portugues/7portugues.html")


def portugues8(request):
    return render(request, "educadigital/portugues/8portugues.html")


def portugues9(request):
    return render(request, "educadigital/portugues/9portugues.html")


def historia(request):
    return render(request, "educadigital/historia.html")


def historia6(request):
    return render(request, "educadigital/historia/6historia.html")


def historia7(request):
    return render(request, "educadigital/historia/7historia.html")


def historia8(request):
    return render(request, "educadigital/historia/8historia.html")


def historia9(request):
    return render(request, "educadigital/historia/9historia.html")


def geografia(request):
    return render(request, "educadigital/geografia.html")


def geografia6(request):
    return render(request, "educadigital/geografia/6geografia.html")


def geografia7(request):
    return render(request, "educadigital/geografia/7geografia.html")


def geografia8(request):
    return render(request, "educadigital/geografia/8geografia.html")


def geografia9(request):
    return render(request, "educadigital/geografia/9geografia.html")


def get_quiz(request):
    category_name = request.GET.get("category")
    limit = request.GET.get("limit")

    questions = Question.objects.select_related("category").all()

    if category_name:
        questions = questions.filter(
            category__category_name__icontains=category_name)

    question_list = list(questions)
    random.shuffle(question_list)

    if limit:
        try:
            limit = int(limit)
            question_list = question_list[:limit]
        except ValueError:
            pass

    data = []
    for question in question_list:
        data.append({
            "uid": str(question.uid),
            "category": question.category.category_name,
            "question": question.question,
            "marks": question.marks,
            "answers": question.get_answers()
        })

    return JsonResponse({
        "status": True,
        "data": data
    })
