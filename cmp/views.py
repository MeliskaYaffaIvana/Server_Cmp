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
        env_template = payload.get('env_template')
        env_kontainer = payload.get('env_kontainer')

        # Mendapatkan path folder user berdasarkan kategori
        user_folder = f"/nfs/{nim}/{kategori}"

        # Membuat direktori user jika belum ada
        os.makedirs(user_folder, exist_ok=True)

        # Perintah untuk membuat kontainer Docker
        docker_cmd = f"docker run -d --name {id} -p {port_kontainer}:{port} -v {user_folder}:{default_dir}"

        # Cek apakah kategori adalah "database" dan env_kontainer tidak kosong
        if kategori == "database" and env_kontainer:
            # Ambil nilai env_template dan env_kontainer secara terpisah
            usertmp = env_template.get('usertmp', '')
            passtmp = env_template.get('passtmp', '')
            rootpasstmp = env_template.get('rootpasstmp', '')
            username = env_kontainer.get('username', '')
            password = env_kontainer.get('password', '')
            rootpass = env_kontainer.get('rootpass', '')

            # Tambahkan setting username, password, dan rootpass ke dalam perintah docker_cmd
            docker_cmd += f" -e usertmp={username} -e passtmp={password} -e rootpasstmp={rootpass}"

        # Menjalankan perintah menggunakan subprocess
        subprocess.run(docker_cmd, shell=True)

        # Lanjutkan dengan operasi lainnya sesuai kebutuhan Anda
        # ...

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
        # Menerima data dari klien
        payload = json.loads(request.body)
        deleted_template_id = payload.get('deleted_template_id')
        deleted_template_link = payload.get('deleted_template_link')

        # Mengambil daftar images dari server
        cmd_images = 'docker images --format "{{.ID}} {{.Repository}}:{{.Tag}}"'
        result_images = subprocess.run(cmd_images, shell=True, capture_output=True, text=True)

        if result_images.returncode != 0:
            return JsonResponse({'error': 'Failed to get images'}, status=500)

        images = result_images.stdout.strip().split('\n')

        for image in images:
            image_parts = image.split(' ')
            image_id = image_parts[0]
            repository_tag = image_parts[1]

            if deleted_template_link in repository_tag:
                cmd_delete = f'docker rmi -f {image_id}'
                subprocess.run(cmd_delete, shell=True, capture_output=True, text=True)

        return JsonResponse({'message': 'Template deletion completed'}, status=200)

    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def delete_kontainer(request):
    if request.method == 'POST':
        payload = request.POST
        id = payload.get('id')

        # Menghapus kontainer dengan menggunakan perintah docker rm
        cmd_delete = f'docker rm {id}'
        result_delete = subprocess.run(cmd_delete, shell=True, capture_output=True, text=True)

        if result_delete.returncode != 0:
            return JsonResponse({'error': 'Failed to delete container'})

        return JsonResponse({'message': 'Container deletion completed'})

    else:
        return JsonResponse({'error': 'Invalid request method'})
    
