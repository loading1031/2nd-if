import uuid
from pathlib import Path

from asgiref.sync import sync_to_async
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


@require_http_methods(["POST"])
async def upload_image(request):
    """EditorJS 이미지 업로드 엔드포인트"""
    if 'image' not in request.FILES:
        return JsonResponse({'success': 0, 'message': '이미지가 없습니다.'})

    image = request.FILES['image']

    # Validate size
    if image.size > MAX_FILE_SIZE:
        return JsonResponse({
            'success': 0,
            'message': '파일 크기가 5MB를 초과합니다.',
        })

    # Validate extension
    file_ext = Path(image.name).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        return JsonResponse({
            'success': 0,
            'message': f'허용되지 않는 파일 형식입니다. 허용: {", ".join(ALLOWED_EXTENSIONS)}',
        })

    # Safe filename
    safe_filename = f'{uuid.uuid4().hex}{file_ext}'
    file_path = f'editor_images/{safe_filename}'

    # Async save
    saved_name = await sync_to_async(default_storage.save)(file_path, image)
    file_url = default_storage.url(saved_name)

    return JsonResponse({
        'success': 1,
        'file': {'url': file_url},
    })
