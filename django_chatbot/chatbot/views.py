import os

import openai
from django.contrib import auth
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from dotenv import load_dotenv

from .models import Chat

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


def ask_openai(message):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an helpful assistant."},
            {"role": "user", "content": message},
        ],
    )

    answer = response.choices[0].message.content.strip()
    return answer


# Create your views here.
def chatbot(request):
    if not request.user.is_authenticated:
        return redirect("login")

    chats = Chat.objects.filter(user=request.user)

    if request.method == "POST":
        message = request.POST.get("message")
        response = ask_openai(message)

        chat = Chat(
            user=request.user,
            message=message,
            response=response,
            created_at=timezone.now(),
        )
        chat.save()
        return JsonResponse({"message": message, "response": response})
    return render(request, "chatbot.html", {"chats": chats})


def login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect("chatbot")
        else:
            error_message = "Invalid username or password"
            return render(
                request,
                "login.html",
                {"error_message": error_message},
            )
    else:
        return render(request, "login.html")


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password1 = request.POST["password1"]
        password2 = request.POST["password2"]

        if password1 == password2:
            try:
                user = User.objects.create_user(username, email, password1)
                user.save()
                auth.login(request, user)
                return redirect("chatbot")
            except IntegrityError:
                error_message = "Username or email already exists"
                return render(
                    request, "register.html", {"error_message": error_message}
                )
        else:
            error_message = "Passwords don't match"
            return render(
                request,
                "register.html",
                {"error_message": error_message},
            )
    return render(request, "register.html")


def logout(request):
    auth.logout(request)
    return redirect("login")
