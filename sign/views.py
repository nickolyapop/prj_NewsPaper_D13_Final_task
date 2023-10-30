import random

from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from .forms import RegisterForm
from .models import TimeCode


@login_required
def profile_view(request):
    return render(request, 'sign/profile.html')


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy("sign:profile")

    def form_valid(self, form):
        user = form.save()
        code = random.choice('qwertyuiopasdfghjklzxcvbnm')
        TimeCode.objects.create(code=code, user=user)
        user_email = form.cleaned_data['email']
        subject = 'Одноразовый код для регистрации'
        message = f'Ваш одноразовый код для регистрации: {code}'
        from_email = 'nickolya212008@yandex.ru'  # Укажите вашу почту здесь
        recipient_list = [user_email]

        send_mail(subject, message, from_email, recipient_list, fail_silently=False)

        user.save()
        return super().form_valid(form)
