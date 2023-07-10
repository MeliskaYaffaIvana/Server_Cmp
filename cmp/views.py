from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import subprocess
import json
from django.http import HttpResponse
from django.db import connection
import os

@csrf_exempt
def update_bolehkan(request):
    if request.method == 'POST':
        # Menerima data dari client
        payload = json.loads(request.body)
        id = payload.get('id', None)
        bolehkan = payload.get('bolehkan', None)
        print (id)
        print(bolehkan)
        # Validasi data
        if id is None or bolehkan is None:
            return JsonResponse({'error': 'Data tidak lengkap'}, status=400)

        # Menjalankan perintah Docker inspect untuk mendapatkan status kontainer
        cmd = ['docker', 'inspect', '--format', '{{.State.Status}}', id]
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(result)
        if result.returncode != 0:
            return JsonResponse({'error': 'Gagal mendapatkan status kontainer'}, status=500)

        status = result.stdout.strip()
        print(status)
        
        # Menentukan status kontainer berdasarkan nilai bolehkan
        print("Masuk ke if-else")
        print("Nilai bolehkan:", bolehkan)
        print("Nilai status:", status)
        if bolehkan == '0' and status == 'running':
            # Jika bolehkan 0 dan status running, menjalankan perintah Docker stop
            cmd_stop = ['docker', 'stop', id]
            print("Eksekusi cmd_stop")
            try:
                subprocess.run(cmd_stop, check=True)
                print(cmd_stop)
            except subprocess.CalledProcessError as e:
                return JsonResponse({'error': 'Gagal menjalankan perintah Docker stop', 'details': str(e)}, status=500)

        elif bolehkan == '1' and status == 'exited':
            # Jika bolehkan 1 dan status exited, menjalankan perintah Docker start
            cmd_start = ['docker', 'start', id]
            print("Eksekusi cmd_start")
            try:
                subprocess.run(cmd_start, check=True)
                print(cmd_start)
            except subprocess.CalledProcessError as e:
                return JsonResponse({'error': 'Gagal menjalankan perintah Docker start', 'details': str(e)}, status=500)

        print("Nilai bolehkan:", bolehkan)
        print("Nilai status:", status)
        print("Cmd stop:", cmd_stop)
        print("Cmd start:", cmd_start)
        # Respon berhasil
        return JsonResponse({'message': 'Status berhasil diperbarui'}, status=200)
    else:
        # Metode HTTP tidak diizinkan
        return JsonResponse({'error': 'Metode HTTP tidak diizinkan'}, status=405)

    
@csrf_exempt
def create_container(request):
    if request.method == 'POST':
        # Mengambil inputan dari permintaan klien
        payload = json.loads(request.body)
        id = payload.get('id')
        nama_template = payload.get('nama_template')
        default_dir = payload.get('default_dir')
        port_kontainer = payload.get('port_kontainer')
        port = payload.get('port')
        nim = payload.get('nim')
        kategori = payload.get('kategori')

        # Mendapatkan path folder user berdasarkan kategori
        user_folder = f"/nfs/{nim}/{kategori}"

        # Membuat direktori user jika belum ada
        os.makedirs(user_folder, exist_ok=True)

        # Perintah untuk membuat kontainer Docker
        docker_cmd = f"docker run -d --name {id} -p {port_kontainer}:{port} -v {user_folder}:{default_dir} {nama_template}"
        print (docker_cmd)
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

