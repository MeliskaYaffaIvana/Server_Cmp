from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import subprocess
import subprocess

@csrf_exempt
def create_template(request):
    if request.method == 'POST':
        # Mengambil inputan dari permintaan klien
        nama_template = request.POST.get('nama_template')
        link_template = request.POST.get('link_template')
        print(nama_template)
        print(link_template)

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


# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from django.db import connection
# import subprocess

# @csrf_exempt
# def create_template(request):
#     if request.method == 'POST':
#         # Mengambil inputan dari permintaan klien
#         nama_template = request.POST.get('nama_template')
#         link_template = request.POST.get('link_template')

#         # Perintah untuk membuat images Docker dari link Docker Hub
#         docker_cmd = f"docker pull {link_template} && docker tag {link_template} {nama_template}"

#         # Menjalankan perintah menggunakan subprocess
#         subprocess.run(docker_cmd, shell=True)

#         # Mengirimkan respon ke klien
#         response = {
#             'status': 'success',
#             'message': 'Template created successfully.'
#         }

#         # # Mengubah status_job menjadi 0 di database
#         # with connection.cursor() as cursor:
#         #     update_query = "UPDATE template SET status_job = 0 WHERE  nama_template = %s"
#         #     cursor.execute(update_query, [nama_template])

#         return JsonResponse(response)

#     else:
#         response = {
#             'status': 'error',
#             'message': 'Invalid request method.'
#         }
#         return JsonResponse(response)

