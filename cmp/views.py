from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import subprocess

@csrf_exempt
def create_template(request):
    if request.method == 'POST':
        # Mengambil inputan dari permintaan klien
        nama_template = request.POST.get('nama_template')
        link_template = request.POST.get('link_template')

        # Mengubah nama_template menjadi lowercase
        nama_template = nama_template.lower()
        print (nama_template)
        print (link_template)
        # Perintah untuk membuat images Docker dari link Docker Hub
        docker_cmd = f"docker pull {link_template} && docker tag {link_template} {nama_template}"

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
