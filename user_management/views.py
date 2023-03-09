from user_management.forms import RegistrationForm
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic.edit import FormView
from django.contrib.auth import login


def dashboard(request):
    return render(request, "registration/dashboard.html")


def registration(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            send_mail('Thanks for registration', f'{username}, your account has been successfully created',
                      'kopitin112@gmail.com', [email], fail_silently=False)
            login(request, user)
            return redirect('dashboard')
    else:
        form = RegistrationForm()
    return render(request, 'registration/registration.html', {'form': form})

# class RegistrationForm(FormView):
#     form_class = SignUpForm
#     template_name = 'registration/registration.html'
#     success_url = reverse('dashboard')
#
#     def form_valid(self, form):
#         user = form.save()
#         login(self.request, user)
#         username = form.cleaned_data['username']
#         email = form.cleaned_data['email']
#         send_mail('Thanks for registration', f'{username}, your account has been successfully created',
#                   'kopitin112@gmail.com', [email], fail_silently=False)
#         return super().form_valid(form)

