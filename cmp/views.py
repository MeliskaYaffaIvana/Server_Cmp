from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import subprocess
import json
from django.http import HttpResponse
from django.db import connection
import os

@csrf_exempt
def create_container(request):
    if request.method == 'POST':
        # Mengambil inputan dari permintaan klien
        nama_kontainer = request.POST.get('nama_kontainer')
        nama_template = request.POST.get('nama_template')
        default_dir = request.POST.get('default_dir')
        nim = request.POST.get('nim')
        kategori = request.POST.get('kategori')

        # Mendapatkan path folder user berdasarkan kategori
        user_folder = f"/nfs/{nim}/{kategori}"

        # Membuat direktori user jika belum ada
        os.makedirs(user_folder, exist_ok=True)

        # Perintah untuk membuat kontainer Docker
        docker_cmd = f"docker run -d --name {nama_kontainer} -p 80:80 -v {user_folder}:{default_dir} {nama_template}"

        # Menjalankan perintah menggunakan subprocess
        subprocess.run(docker_cmd, shell=True)

        return HttpResponse("Container created successfully.")

    else:
        return HttpResponse("Invalid request method.")

@csrf_exempt
def create_template(request):
    if request.method == 'POST':
        # Mengambil inputan dari permintaan klien
        payload = json.loads(request.body)
        nama_template = payload.get('nama_template')
        link_template = payload.get('link_template')

        # Parsing the repository and tag from the link
        repository, tag = link_template.split(':')
        repository = repository.lower()  # Converting repository name to lowercase

        # Creating the new image reference with lowercase repository name
        new_image_ref = f"{repository}:{tag}"

        # Perintah untuk melakukan docker pull dengan image reference yang sudah dimodifikasi
        docker_cmd = f"docker pull {new_image_ref} && docker tag {new_image_ref} {nama_template}"

        # Menjalankan perintah menggunakan subprocess
        subprocess.run(docker_cmd, shell=True)

        # Mengirimkan respon ke klien
        response = {
            'status': 'success',
            'message': 'Template created successfully.'
        }

        return JsonResponse(response)

    else:
        response = {
            'status': 'error',
            'message': 'Invalid request method.'
        }
        return JsonResponse(response)

