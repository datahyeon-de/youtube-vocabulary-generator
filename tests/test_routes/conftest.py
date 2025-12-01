"""
테스트용 라우트 관련 fixture

이 파일은 tests/test_routes/ 폴더에서만 사용되는 fixture를 정의합니다.
라우트 테스트에서 공통으로 사용하는 테스트 데이터를 제공합니다.

사용 위치:
    - tests/test_routes/test_video.py: POST /api/video 엔드포인트 테스트
    
테스트 대상:
    - app/routes/video.py의 POST /api/video 엔드포인트
    - 실제 서버 통신 테스트
"""
import pytest
import httpx


@pytest.fixture
def sample_youtube_url():
    """정상적인 YouTube URL (전체 URL 형식)
    
    사용 위치:
        - tests/test_routes/test_video.py: 정상 케이스 테스트
    
    테스트 대상:
        - app/routes/video.py의 POST /api/video 엔드포인트
        - 정상적인 YouTube URL 입력 시 200 OK 응답 확인
    """
    return "https://www.youtube.com/watch?v=dQw4w9WgXcQ"


@pytest.fixture
def empty_string():
    """빈 문자열 (에러 케이스용)
    
    사용 위치:
        - tests/test_routes/test_video.py: 스키마 검증 실패 테스트
    
    테스트 대상:
        - app/models/schemas.py의 validate_url_not_empty 검증
        - 빈 문자열 입력 시 422 에러 반환 확인
    """
    return ""


@pytest.fixture
def invalid_url_format_text():
    """텍스트만 있는 값 (에러 케이스용)
    
    사용 위치:
        - tests/test_routes/test_video.py: 스키마 검증 실패 테스트
    
    테스트 대상:
        - app/models/schemas.py의 validate_url_format 검증
        - 텍스트만 입력 시 422 에러 반환 확인
    """
    return "그냥 텍스트"


@pytest.fixture
def invalid_url_format_no_scheme():
    """scheme(http://) 없는 URL (에러 케이스용)
    
    사용 위치:
        - tests/test_routes/test_video.py: 스키마 검증 실패 테스트
    
    테스트 대상:
        - app/models/schemas.py의 validate_url_format 검증
        - scheme 없는 URL 입력 시 422 에러 반환 확인
    """
    return "youtube.com"


@pytest.fixture
def sample_video_id():
    """정상적인 YouTube Video ID (자막이 있는 영상)
    
    사용 위치:
        - tests/test_routes/test_video.py: POST /api/video/{video_id}/transcript 정상 케이스 테스트
    
    테스트 대상:
        - app/routes/video.py의 POST /api/video/{video_id}/transcript 엔드포인트
        - 자막이 있는 영상으로 자막 추출 성공 확인
    """
    return "dQw4w9WgXcQ"  # Rick Astley - Never Gonna Give You Up (자막 있음)


@pytest.fixture
def invalid_video_id():
    """존재하지 않는 YouTube Video ID (에러 케이스용)
    
    사용 위치:
        - tests/test_routes/test_video.py: POST /api/video/{video_id}/transcript 에러 케이스 테스트
    
    테스트 대상:
        - app/routes/video.py의 POST /api/video/{video_id}/transcript 엔드포인트
        - 존재하지 않는 영상 ID 입력 시 400 에러 반환 확인
    """
    return "INVALID_VIDEO_ID_12345"


@pytest.fixture(scope="session")
def server_available():
    """FastAPI 서버가 실행 중인지 확인하는 fixture
    
    Returns:
        bool: 서버가 사용 가능하면 True, 아니면 False
        
    확인 방법:
        - /health 엔드포인트로 서버 실행 여부 확인
        - 기본 포트: 8000 (tests/conftest.py의 running_server_client와 동일)
        
    사용 예시:
        @pytest.mark.skipif(not server_available(), reason="서버가 실행 중이지 않습니다")
        def test_endpoint(server_available, running_server_client):
            # 테스트 코드
    """
    try:
        base_url = "http://localhost:8000"
        with httpx.Client(base_url=base_url, timeout=5.0) as client:
            try:
                response = client.get("/health", timeout=2.0)
                if response.status_code == 200:
                    return True
            except (httpx.ConnectError, httpx.TimeoutException, httpx.NetworkError):
                return False
            except Exception:
                return False
    except Exception:
        return False
    return False


@pytest.fixture
def skip_if_server_unavailable(server_available):
    """서버가 사용 불가능하면 테스트를 자동으로 스킵하는 fixture
    
    사용 위치:
        - tests/test_routes/test_video.py: 실행 중인 서버가 필요한 테스트
    
    사용 예시:
        def test_endpoint(skip_if_server_unavailable, running_server_client):
            # 서버가 없으면 자동으로 스킵됨
            # 테스트 코드
    """
    if not server_available:
        pytest.skip("서버가 실행 중이지 않습니다. 'uvicorn app.main:app --reload' 명령어로 서버를 실행해주세요.")
    return True

