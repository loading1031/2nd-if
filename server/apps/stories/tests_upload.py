import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import AsyncClient


@pytest.fixture
async def client():
    return AsyncClient()


@pytest.mark.django_db(transaction=True)
class TestImageUpload:
    async def test_upload_success(self, client):
        """정상적인 PNG 이미지 업로드"""
        png_header = b'\x89PNG\r\n\x1a\n' + b'\x00' * 100
        image = SimpleUploadedFile('test.png', png_header, content_type='image/png')
        response = await client.post('/api/upload-image/', {'image': image})
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == 1
        assert 'url' in data['file']

    async def test_upload_no_file(self, client):
        """파일 없이 요청 시 실패"""
        response = await client.post('/api/upload-image/')
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == 0

    async def test_upload_invalid_extension(self, client):
        """허용되지 않는 확장자 업로드 시 실패"""
        file = SimpleUploadedFile(
            'test.exe', b'data', content_type='application/octet-stream'
        )
        response = await client.post('/api/upload-image/', {'image': file})
        data = response.json()
        assert data['success'] == 0
        assert '허용되지 않는' in data['message']

    async def test_upload_too_large(self, client):
        """5MB 초과 파일 업로드 시 실패"""
        large_data = b'\x89PNG\r\n\x1a\n' + b'\x00' * (6 * 1024 * 1024)
        file = SimpleUploadedFile('big.png', large_data, content_type='image/png')
        response = await client.post('/api/upload-image/', {'image': file})
        data = response.json()
        assert data['success'] == 0
        assert '5MB' in data['message']
