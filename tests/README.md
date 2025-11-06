# FastAPI 테스트 가이드

FastAPI 프로젝트에서 `tests/` 폴더를 활용하는 방법에 대한 가이드입니다.

## 📁 테스트 폴더 구조

```
tests/
├── __init__.py
├── conftest.py              # pytest 설정 및 공통 fixture
├── test_main.py            # FastAPI 앱 메인 테스트
├── test_routes/            # 라우트별 테스트
│   ├── __init__.py
│   └── test_video.py      # 비디오 관련 엔드포인트 테스트
├── test_services/          # 서비스 로직 테스트
│   ├── __init__.py
│   ├── test_validator.py   # 링크 검증 테스트
│   └── test_transcript.py # 자막 추출 테스트
└── test_models/            # 모델/스키마 테스트
    ├── __init__.py
    └── test_schemas.py     # Pydantic 스키마 테스트
```

## 🧪 테스트 종류

### 1. 단위 테스트 (Unit Tests)
- 개별 함수나 메서드의 동작을 테스트
- Mock을 사용하여 외부 의존성 제거
- 예: `test_validator.py`, `test_schemas.py`

### 2. 통합 테스트 (Integration Tests)
- 여러 컴포넌트가 함께 작동하는지 테스트
- 실제 데이터베이스나 외부 API 사용 (또는 Mock)
- 예: `test_transcript.py` (자막 추출 서비스)

### 3. API 테스트 (E2E Tests)
- FastAPI 엔드포인트 전체 플로우 테스트
- `httpx`를 사용한 HTTP 요청/응답 테스트
- 예: `test_video.py` (비디오 관련 API)

## 🛠️ 기본 설정

### conftest.py
`conftest.py`는 pytest의 설정 파일로, 모든 테스트에서 공통으로 사용할 fixture를 정의합니다.

**주요 내용:**
- TestClient 설정 (FastAPI 앱 인스턴스)
- 공통 Mock 데이터
- 테스트용 데이터베이스 설정 (필요시)
- 테스트 전/후 처리 (setup/teardown)

### 예시: conftest.py

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    """FastAPI 테스트 클라이언트"""
    return TestClient(app)

@pytest.fixture
def sample_youtube_url():
    """테스트용 YouTube URL"""
    return "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

@pytest.fixture
def sample_video_id():
    """테스트용 Video ID"""
    return "dQw4w9WgXcQ"
```

## 📝 테스트 파일 작성 예시

### 예시 1: 라우트 테스트 (test_routes/test_video.py)

```python
import pytest
from fastapi.testclient import TestClient


def test_video_endpoint_post_success(client: TestClient):
    """POST /api/video 엔드포인트 성공 테스트"""
    response = client.post(
        "/api/video",
        json={"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}
    )
    assert response.status_code == 200
    assert "video_id" in response.json()


def test_video_endpoint_post_invalid_url(client: TestClient):
    """잘못된 URL 형식 테스트"""
    response = client.post(
        "/api/video",
        json={"url": "invalid-url"}
    )
    assert response.status_code == 400
    assert "error" in response.json()


def test_video_endpoint_get(client: TestClient, sample_video_id):
    """GET /api/video/{video_id} 엔드포인트 테스트"""
    response = client.get(f"/api/video/{sample_video_id}")
    assert response.status_code == 200
```

### 예시 2: 서비스 테스트 (test_services/test_validator.py)

```python
import pytest
from app.services.validator import validate_youtube_url, extract_video_id


def test_validate_youtube_url_success():
    """유효한 YouTube URL 검증 테스트"""
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    assert validate_youtube_url(url) == True


def test_validate_youtube_url_invalid():
    """잘못된 URL 검증 테스트"""
    url = "https://invalid.com"
    assert validate_youtube_url(url) == False


def test_extract_video_id():
    """Video ID 추출 테스트"""
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    assert extract_video_id(url) == "dQw4w9WgXcQ"
```

### 예시 3: Mock을 사용한 외부 API 테스트

```python
from unittest.mock import patch, Mock
import pytest
from app.services.transcript import extract_transcript


@patch('app.services.transcript.youtube_transcript_api')
def test_extract_transcript_success(mock_transcript_api):
    """자막 추출 성공 테스트 (Mock 사용)"""
    # Mock 데이터 설정
    mock_transcript_api.get_transcript.return_value = [
        {"text": "Hello", "start": 0.0, "duration": 2.0},
        {"text": "World", "start": 2.0, "duration": 2.0}
    ]
    
    result = extract_transcript("dQw4w9WgXcQ")
    assert len(result) == 2
    assert result[0]["text"] == "Hello"
```

## 🚀 테스트 실행 방법

### 모든 테스트 실행
```bash
pytest
```

### 특정 테스트 파일 실행
```bash
pytest tests/test_routes/test_video.py
```

### 특정 테스트 함수 실행
```bash
pytest tests/test_routes/test_video.py::test_video_endpoint_post_success
```

### 테스트 커버리지 확인
```bash
pytest --cov=app tests/
```

### 상세 출력 모드
```bash
pytest -v
```

### 실패한 테스트만 재실행
```bash
pytest --lf
```

## 📋 테스트 작성 가이드

### 테스트 함수 네이밍 규칙
- 함수명은 `test_`로 시작해야 함
- 테스트하는 기능을 명확히 표현: `test_validate_youtube_url_success`

### 테스트 구조 (AAA 패턴)
```python
def test_function_name():
    # Arrange (준비): 테스트 데이터 준비
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    # Act (실행): 테스트할 함수 실행
    result = validate_youtube_url(url)
    
    # Assert (검증): 결과 확인
    assert result == True
```

### 주의사항
1. **독립성**: 각 테스트는 다른 테스트에 의존하지 않아야 함
2. **재현 가능성**: 같은 입력에 대해 항상 같은 결과가 나와야 함
3. **빠른 실행**: 테스트는 빠르게 실행되어야 함
4. **명확한 실패 메시지**: 실패 시 무엇이 잘못되었는지 알 수 있어야 함

## 🔗 참고 자료

- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)

