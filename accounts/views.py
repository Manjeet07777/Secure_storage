from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
import os

from .models import StoredFile
from .utils import encrypt_file, decrypt_file

# 📌 Home Page
def home_view(request):
    return render(request, "index.html")

# 📌 User Registration
def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = UserCreationForm()
    return render(request, "register.html", {"form": form})

# 📌 User Login
def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("home")
    else:
        form = AuthenticationForm()
    return render(request, "login.html", {"form": form})

# 📌 User Logout
def logout_view(request):
    logout(request)
    return redirect("home")

# 📌 Upload & Encrypt File
@login_required
def upload_file_view(request):
    if request.method == "POST":
        uploaded_file = request.FILES.get("file")
        key = request.POST.get("key")

        if not uploaded_file:
            return render(request, "upload.html", {"error": "❌ Please select a file to upload."})
        if not key:
            return render(request, "upload.html", {"error": "❌ Please enter an encryption key."})

        fs = FileSystemStorage()
        filename = fs.save(uploaded_file.name, uploaded_file)
        file_path = fs.path(filename)

        try:
            encrypt_file(file_path, key)
            StoredFile.objects.create(
                user=request.user,
                original_filename=uploaded_file.name,
                stored_filename=filename,
            )
            return render(request, "upload.html", {"message": "✅ File uploaded & encrypted successfully!"})
        except Exception as e:
            if os.path.exists(file_path):
                os.remove(file_path)
            return render(request, "upload.html", {"error": f"❌ Error: {str(e)}"})

    return render(request, "upload.html")

# 📌 User File History
@login_required
def history_view(request):
    files = StoredFile.objects.filter(user=request.user)
    return render(request, "history.html", {"files": files})

# 📌 Download & Decrypt File
@login_required
def download_file_view(request, file_id):
    fs = FileSystemStorage()

    try:
        # Try to get the file for the logged-in user
        file_obj = StoredFile.objects.get(id=file_id, user=request.user)
        owner = True
    except StoredFile.DoesNotExist:
        # Non-owner access: fetch file record anyway
        file_obj = get_object_or_404(StoredFile, id=file_id)
        owner = False

    file_path = fs.path(file_obj.stored_filename)

    if not owner:
        # Serve the encrypted file directly for non-owners
        with open(file_path, "rb") as f:
            response = HttpResponse(f.read(), content_type="application/octet-stream")
            response['Content-Disposition'] = f'attachment; filename="{file_obj.original_filename}.enc"'
            return response

    # Owner workflow: prompt for key
    if request.method == "POST":
        key = request.POST.get("key")
        decrypted_filename = f"decrypted_{file_obj.original_filename}"
        decrypted_path = fs.path(decrypted_filename)

        try:
            decrypt_file(file_path, decrypted_path, key)
            file_url = fs.url(decrypted_filename)
            return render(request, "download.html", {"file": file_obj, "file_url": file_url})
        except Exception:
            return render(request, "enter_key.html", {"file": file_obj, "error": "❌ Wrong decryption key! Try again."})

    return render(request, "enter_key.html", {"file": file_obj})
# 📌 Delete File
@login_required
def delete_file_view(request, file_id):
    file_obj = get_object_or_404(StoredFile, id=file_id, user=request.user)
    fs = FileSystemStorage()
    file_path = fs.path(file_obj.stored_filename)

    if os.path.exists(file_path):
        os.remove(file_path)

    decrypted_path = fs.path(f"decrypted_{file_obj.original_filename}")
    if os.path.exists(decrypted_path):
        os.remove(decrypted_path)

    file_obj.delete()
    return redirect("history")
