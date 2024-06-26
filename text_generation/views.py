
import openai
from django.shortcuts import render
from django.http import JsonResponse
import os
from django.conf import settings
from django.core.files.storage import default_storage
from .models import ImageInfo
import base64
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv

load_dotenv()

key = os.environ['OPENAI_API_KEY']

client = openai.OpenAI(api_key=key)

def view_all_data(request):
    image_infos = ImageInfo.objects.all()
    context = {
        'image_infos': image_infos
    }
    print(os.environ.get("OPENAI_API_KEY"))
    return render(request, 'view_all_data.html', context)

def deleteall_record(request):
    images = ImageInfo.objects.all()
    for image in images:
        image.delete()
        image_path = os.path.join(settings.MEDIA_ROOT, str(image.image))
        if os.path.isfile(image_path):
            os.remove(image_path)
    return render(request, 'upload.html')

def home(request):
    return render(request, 'upload.html')

@csrf_exempt
def upload_file(request):
    if request.method == 'POST' and 'image' in request.FILES:
        image = request.FILES['image']
        image_path = os.path.join(settings.MEDIA_ROOT, image.name)
        try:
            with open(image_path, 'wb+') as destination:
                for chunk in image.chunks():
                    destination.write(chunk)
            with open(image_path, "rb") as img_file:
                base64_image = base64.b64encode(img_file.read()).decode('utf-8')
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "please describe the objects in the image, mention their color and height&width of object in the image in centimeters.The examples are (dog,black,23x40, cat,white,10x20, etc.) please provide the answer only the format as I mentioned in the examples.if there are too many objects then give only the name big object, its color and height&width in the example format."},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpg;base64,{base64_image}",
                                }
                            },
                        ],
                    }
                ],
                max_tokens=800,
            )
            description = response.choices[0].message.content
            data = description.split(',')
            print (data)
            what_the_image_is = data[0]
            color = data[1]
            height_and_width=data[2]
            height=data[2].split('x')[0]
            width=data[2].split('x')[1]
            dimensions=f"Height={height} , width={width}"
            image_info = ImageInfo.upload_or_update_image(image=image, what_the_image_is=what_the_image_is, color=color, dimensions=dimensions)
            os.remove(image_path)
            return JsonResponse({'object': what_the_image_is, 'color':color, 'height&width':height_and_width,'image_info_quantity': image_info.quantity})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return render(request, 'upload.html')

def transcribe_audio(request):
    if request.method == 'POST' and 'file' in request.FILES:
        file = request.FILES['file']
        file_path = "media/" + default_storage.save(file.name, file)
        try:
            with open(file_path, 'rb') as audio_file:
                transcript = client.audio.transcriptions.create(model="whisper-1", file=audio_file, language="en")
            os.remove(file_path)
            return JsonResponse({'transcript': transcript.text})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request'}, status=400)
