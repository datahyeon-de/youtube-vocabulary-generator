"""
테스트용 모델/스키마 관련 fixture

이 파일은 tests/test_models/ 폴더에서만 사용되는 fixture를 정의합니다.
모델/스키마 테스트에서 공통으로 사용하는 테스트 데이터를 제공합니다.

사용 위치:
    - tests/test_models/test_schemas.py: VideoUrlRequest 스키마 테스트
    
테스트 대상:
    - app/models/schemas.py의 VideoUrlRequest 스키마
    - URL 검증 로직 (validate_url_not_empty, validate_url_format, validate_youtube_url)
"""
import pytest


@pytest.fixture
def sample_youtube_url():
    """정상적인 YouTube URL (전체 URL 형식)
    
    사용 위치:
        - tests/test_models/test_schemas.py: 정상 케이스 테스트
    
    테스트 대상:
        - app/models/schemas.py의 VideoUrlRequest 스키마
        - 모든 검증 로직이 통과하는 정상 케이스
    
    사용 예시:
        def test_success(sample_youtube_url):
            data = VideoUrlRequest(url=sample_youtube_url)
            assert data.url == sample_youtube_url
    """
    return "https://www.youtube.com/watch?v=dQw4w9WgXcQ"


@pytest.fixture
def sample_youtube_short_url():
    """youtu.be 형식의 YouTube URL (에러 케이스용)
    
    사용 위치:
        - tests/test_models/test_schemas.py: YouTube URL 형식 검증 테스트
    
    테스트 대상:
        - app/models/schemas.py의 validate_youtube_url 검증
        - www.youtube.com/watch?v= 형식만 허용하므로 이 형식은 에러 발생
    
    사용 예시:
        def test_youtube_short_url(sample_youtube_short_url):
            with pytest.raises(ValidationError):
                VideoUrlRequest(url=sample_youtube_short_url)
    """
    return "https://youtu.be/dQw4w9WgXcQ"


@pytest.fixture
def sample_video_id():
    """Video ID만 추출된 값
    
    사용 위치:
        - tests/test_models/test_schemas.py: 필요시 사용
        - tests/test_services/: Video ID 추출 함수 테스트 (향후)
    
    테스트 대상:
        - Video ID 관련 로직 테스트
    """
    return "dQw4w9WgXcQ"


@pytest.fixture
def invalid_url():
    """YouTube가 아닌 URL (에러 케이스용)
    
    사용 위치:
        - tests/test_models/test_schemas.py: YouTube URL 형식 검증 테스트
    
    테스트 대상:
        - app/models/schemas.py의 validate_youtube_url 검증
        - YouTube URL만 허용하므로 다른 도메인은 에러 발생
    
    사용 예시:
        def test_non_youtube_url(invalid_url):
            with pytest.raises(ValidationError):
                VideoUrlRequest(url=invalid_url)
    """
    return "https://invalid-url.com"


@pytest.fixture
def empty_string():
    """빈 문자열 (에러 케이스용)
    
    사용 위치:
        - tests/test_models/test_schemas.py: 빈 값 검증 테스트
    
    테스트 대상:
        - app/models/schemas.py의 validate_url_not_empty 검증
        - 빈 문자열이 입력되면 에러 발생해야 함
    
    사용 예시:
        def test_empty_string(empty_string):
            with pytest.raises(ValidationError):
                VideoUrlRequest(url=empty_string)
    """
    return ""


@pytest.fixture
def whitespace_only():
    """공백만 있는 문자열 (에러 케이스용)
    
    사용 위치:
        - tests/test_models/test_schemas.py: 빈 값 검증 테스트
    
    테스트 대상:
        - app/models/schemas.py의 validate_url_not_empty 검증
        - 공백만 있는 경우도 에러 발생해야 함
    
    사용 예시:
        def test_whitespace_only(whitespace_only):
            with pytest.raises(ValidationError):
                VideoUrlRequest(url=whitespace_only)
    """
    return "   "


@pytest.fixture
def invalid_url_format_text():
    """텍스트만 있는 값 (에러 케이스용)
    
    사용 위치:
        - tests/test_models/test_schemas.py: URL 형식 검증 테스트
    
    테스트 대상:
        - app/models/schemas.py의 validate_url_format 검증
        - URL 형식이 아니면 에러 발생해야 함
    
    사용 예시:
        def test_text_only(invalid_url_format_text):
            with pytest.raises(ValidationError):
                VideoUrlRequest(url=invalid_url_format_text)
    """
    return "그냥 텍스트"


@pytest.fixture
def invalid_url_format_no_scheme():
    """scheme(http://) 없는 URL (에러 케이스용)
    
    사용 위치:
        - tests/test_models/test_schemas.py: URL 형식 검증 테스트
    
    테스트 대상:
        - app/models/schemas.py의 validate_url_format 검증
        - scheme이 없으면 에러 발생해야 함
    
    사용 예시:
        def test_no_scheme(invalid_url_format_no_scheme):
            with pytest.raises(ValidationError):
                VideoUrlRequest(url=invalid_url_format_no_scheme)
    """
    return "youtube.com"


@pytest.fixture
def youtube_url_without_www():
    """www 없이 youtube.com만 있는 URL (에러 케이스용)
    
    사용 위치:
        - tests/test_models/test_schemas.py: YouTube URL 형식 검증 테스트
    
    테스트 대상:
        - app/models/schemas.py의 validate_youtube_url 검증
        - 정확히 www.youtube.com만 허용하므로 www 없으면 에러 발생
    
    사용 예시:
        def test_no_www(youtube_url_without_www):
            with pytest.raises(ValidationError):
                VideoUrlRequest(url=youtube_url_without_www)
    """
    return "https://youtube.com/watch?v=dQw4w9WgXcQ"


@pytest.fixture
def youtube_url_wrong_path():
    """잘못된 경로(/embed)를 가진 YouTube URL (에러 케이스용)
    
    사용 위치:
        - tests/test_models/test_schemas.py: YouTube URL 형식 검증 테스트
    
    테스트 대상:
        - app/models/schemas.py의 validate_youtube_url 검증
        - 정확히 /watch 경로만 허용하므로 다른 경로는 에러 발생
    
    사용 예시:
        def test_wrong_path(youtube_url_wrong_path):
            with pytest.raises(ValidationError):
                VideoUrlRequest(url=youtube_url_wrong_path)
    """
    return "https://www.youtube.com/embed/dQw4w9WgXcQ"


@pytest.fixture
def youtube_url_no_v_param():
    """v 파라미터가 없는 YouTube URL (에러 케이스용)
    
    사용 위치:
        - tests/test_models/test_schemas.py: YouTube URL 형식 검증 테스트
    
    테스트 대상:
        - app/models/schemas.py의 validate_youtube_url 검증
        - v= 파라미터가 없으면 에러 발생해야 함
    
    사용 예시:
        def test_no_v_param(youtube_url_no_v_param):
            with pytest.raises(ValidationError):
                VideoUrlRequest(url=youtube_url_no_v_param)
    """
    return "https://www.youtube.com/watch"

