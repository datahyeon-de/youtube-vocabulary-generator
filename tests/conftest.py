"""
pytest 설정 및 공통 fixture

이 파일은 tests/ 폴더 전체에서 사용되는 공통 fixture를 정의합니다.
특정 모듈에서만 사용되는 fixture는 해당 모듈의 conftest.py에 작성하세요.

사용 위치:
- tests/test_main.py: FastAPI 앱 전체 테스트
- tests/test_models/: 모델/스키마 테스트 (일부 fixture 사용)
- tests/test_routes/: 라우트 테스트 (일부 fixture 사용)
- tests/test_services/: 서비스 테스트 (일부 fixture 사용)
"""
import pytest
import httpx
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """FastAPI 테스트 클라이언트 (서버 없이 인메모리 테스트)
    
    사용 위치:
        - tests/test_main.py: FastAPI 엔드포인트 테스트
        - tests/test_routes/: 라우트별 API 테스트
    
    테스트 대상:
        - app/main.py의 FastAPI 앱 전체
        - 모든 API 엔드포인트의 요청/응답 테스트
    
    사용 예시:
        def test_endpoint(client: TestClient):
            response = client.get("/health")
            assert response.status_code == 200
    """
    return TestClient(app)


@pytest.fixture
def running_server_client():
    """이미 실행 중인 서버에 HTTP 요청을 보내는 클라이언트
    
    사용 위치:
        - tests/test_main.py: 실제 서버가 실행 중일 때 테스트
    
    테스트 대상:
        - 실제로 실행 중인 uvicorn 서버 (app/main.py)
        - 네트워크 레벨의 통합 테스트
    
    사용법:
        1. 터미널에서 서버 실행: uvicorn app.main:app --reload
        2. 다른 터미널에서 pytest 실행: pytest tests/test_main.py -k "running_server"
        3. 테스트 코드에서 이 fixture 사용하면 실행 중인 서버로 요청 보냄
    
    주의사항:
        - 서버가 실행 중이어야 함
        - 기본 포트: 8000 (다른 포트면 conftest.py에서 수정 필요)
    """
    # 기본적으로 localhost:8000으로 설정
    # 서버가 다른 포트에서 실행 중이면 여기 수정
    base_url = "http://localhost:8000"
    
    with httpx.Client(base_url=base_url, timeout=10.0) as client:
        yield client

