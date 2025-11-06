"""
pytest 설정 및 공통 fixture
"""
import pytest
import httpx
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """FastAPI 테스트 클라이언트 (서버 없이 인메모리 테스트)"""
    return TestClient(app)


@pytest.fixture
def running_server_client():
    """이미 실행 중인 서버에 HTTP 요청을 보내는 클라이언트
    
    사용법:
    1. 터미널에서 서버 실행: uvicorn app.main:app --reload
    2. pytest 실행: pytest tests/test_main.py
    3. 테스트 코드에서 이 fixture 사용하면 실행 중인 서버로 요청 보냄
    """
    # 기본적으로 localhost:8000으로 설정
    # 서버가 다른 포트에서 실행 중이면 여기 수정
    base_url = "http://localhost:8000"
    
    with httpx.Client(base_url=base_url, timeout=10.0) as client:
        yield client


@pytest.fixture
def sample_youtube_url():
    """테스트용 YouTube URL (전체 URL 형식)"""
    return "https://www.youtube.com/watch?v=dQw4w9WgXcQ"


@pytest.fixture
def sample_youtube_short_url():
    """테스트용 YouTube Short URL"""
    return "https://youtu.be/dQw4w9WgXcQ"


@pytest.fixture
def sample_video_id():
    """테스트용 Video ID"""
    return "dQw4w9WgXcQ"


@pytest.fixture
def invalid_url():
    """테스트용 잘못된 URL"""
    return "https://invalid-url.com"

