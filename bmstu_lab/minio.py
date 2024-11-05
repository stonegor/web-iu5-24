from django.conf import settings
from minio import Minio
from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework.response import Response


def process_file_upload(file_object: InMemoryUploadedFile, client, image_name):
    try:
        client.put_object(
            'bmstu-lab', image_name, file_object, file_object.size)
        return f"http://{settings.AWS_S3_ENDPOINT_URL}/bmstu-lab/{image_name}"
    except Exception as e:
        return {"error": str(e)}


def add_pic(tool, pic):
    client = Minio(
        endpoint=settings.AWS_S3_ENDPOINT_URL,
        access_key=settings.AWS_ACCESS_KEY_ID,
        secret_key=settings.AWS_SECRET_ACCESS_KEY,
        secure=settings.MINIO_USE_SSL
    )
    img_obj_name = f"tool_{tool.id}.png"

    if not pic:
        return Response({"error": "Нет файла для изображения инструмента."})

    result = process_file_upload(pic, client, img_obj_name)

    if isinstance(result, dict) and 'error' in result:
        return Response(result)

    tool.image_url = result
    tool.save()

    return Response({"message": "success"})
