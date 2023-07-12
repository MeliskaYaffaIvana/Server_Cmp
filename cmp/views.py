from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import subprocess
import json
from django.http import HttpResponse
import os

@csrf_exempt
def update_bolehkan(request):
    if request.method == 'POST':
        # Menerima data dari client
        payload = json.loads(request.body)
        id = payload.get('id')
        bolehkan = payload.get('bolehkan')

        # Validasi data
        if id is None or bolehkan is None:
            return JsonResponse({'error': 'Data tidak lengkap'}, status=400)
        
        
        # Menjalankan perintah Docker inspect untuk mendapatkan status kontainer
        cmd = ['docker', 'inspect', '--format', '{{.State.Status}}', id]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            return JsonResponse({'error': 'Gagal mendapatkan status kontainer'}, status=500)

        status = result.stdout.strip()
        print(status)
        
        # Menentukan status kontainer berdasarkan nilai bolehkan
        print("Nilai bolehkan:", bolehkan)
        print("Nilai status:", status)
        cmd_stop = ['docker', 'stop', id]
        cmd_start = ['docker', 'start', id]

        if bolehkan == 0 and status == 'running':
            # Jika bolehkan 0 dan status running, menjalankan perintah Docker stop
            try:
                subprocess.run(cmd_stop, check=True)
                print("Perintah Docker stop berhasil dijalankan:", cmd_stop)
            except subprocess.CalledProcessError as e:
                return JsonResponse({'error': 'Gagal menjalankan perintah Docker stop', 'details': str(e)}, status=500)

        elif bolehkan == 1 and status == 'exited':
            # Jika bolehkan 1 dan status exited, menjalankan perintah Docker start
            try:
                subprocess.run(cmd_start, check=True)
                print("Perintah Docker start berhasil dijalankan:", cmd_start)
            except subprocess.CalledProcessError as e:
                return JsonResponse({'error': 'Gagal menjalankan perintah Docker start', 'details': str(e)}, status=500)

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


@csrf_exempt
def delete_template(request):
    if request.method == 'POST':
        # Menerima data dari client
        payload = json.loads(request.body)
        nama_template = payload.get('nama_template')

        # Menemukan repository images dengan tag "latest" yang tidak sesuai dengan nama_template
        cmd = 'docker images --format "{{.ID}}:{{.Repository}}:{{.Tag}}" --filter "reference={}:\""'
        result = subprocess.run(cmd.format(nama_template), shell=True, capture_output=True, text=True)

        # Memeriksa kesesuaian repository dengan nama_template
        if result.stdout.strip():
            for line in result.stdout.strip().split('\n'):
                repo_id, repo_name, repo_tag = line.split(':')
                if repo_name != nama_template:
                    # Menghapus repository dengan nama repository dan tag yang ditemukan
                    repo_name_tag = f'{repo_name}:{repo_tag}'
                    cmd_hapus = ['docker', 'rmi', repo_name_tag]
                    subprocess.run(cmd_hapus, capture_output=True, text=True)

        # Respon sukses
        return JsonResponse({'message': 'Data diterima'}, status=200)
    else:
        # Metode HTTP tidak diizinkan
        return JsonResponse({'error': 'Metode HTTP tidak diizinkan'}, status=405)

# @csrf_exempt
# def delete_kontainer(request):
#     if request.method == 'POST':
#         # Menerima data dari client
#         payload = json.loads(request.body)
#         id = payload.get('id')

#         # Menemukan repository images berdasarkan nama_template
#         cmd = 'docker images --format "{{.Repository}}"'
#         result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
#         print(result)

#         # Memeriksa kesesuaian repository images dengan nama_template
#         if nama_template not in result.stdout.split('\n'):
#             # Mencari ID template berdasarkan nama_repository
#             cmd_id = 'docker images --format "{{.ID}}" | grep "{}"'.format(nama_template)
#             result_id = subprocess.run(cmd_id, shell=True, capture_output=True, text=True)
#             print(result_id)

#             # Memeriksa apakah output result_id.stdout berisi ID template yang valid
#             if result_id.stdout.strip() != '':
#                 # Mendapatkan ID template yang sesuai
#                 id_template = result_id.stdout.strip()

#                 # Mendapatkan nama repository images yang sesuai dengan ID template
#                 cmd_repo_name = 'docker inspect --format "{{index .RepoTags 0}}" {}'.format(id_template)
#                 result_repo_name = subprocess.run(cmd_repo_name, shell=True, capture_output=True, text=True)
#                 print(result_repo_name)

#                 # Menghapus template jika ada kesesuaian yang tidak sesuai dengan database
#                 if result_repo_name.stdout.strip() != nama_template and result_id.stdout.strip() not in result_repo_name.stdout.strip():
#                     # Jalankan perintah hapus template sesuai dengan ID template
#                     cmd_hapus = ['docker', 'rmi', result_id.stdout.strip()]
#                     subprocess.run(cmd_hapus, capture_output=True, text=True)
#         # Respon sukses
#         return JsonResponse({'message': 'Data diterima'}, status=200)
#     else:
#         # Metode HTTP tidak diizinkan
#         return JsonResponse({'error': 'Metode HTTP tidak diizinkan'}, status=405)