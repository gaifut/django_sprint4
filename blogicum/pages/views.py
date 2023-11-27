from django.shortcuts import render


def about(request):
    return render(request, 'pages/about.html')


def rules(request):
    return render(request, 'pages/rules.html')


def page_not_found_404(request, exception):
    return render(request, 'pages/404.html', status=404)


def csrf_403(request, exception):
    return render(request, 'pages/403csrf.html', status=404)


def server_error_500(request):
    return render(request, 'pages/500.html', status=404)
