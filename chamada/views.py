from django.shortcuts import render


def chamada(request):
    return render(request, "chamada/chamada.html")


def configuracao(request):
    return render(request, "chamada/configuracao.html")


def qrcode(request):
    return render(request, "chamada/qrcode.html")


def turmas(request):
    return render(request, "chamada/turmas.html")


def professor(request):
    return render(request, "chamada/professor.html")
