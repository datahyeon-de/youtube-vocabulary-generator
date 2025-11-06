"""
Pydantic 스키마 테스트
"""
import pytest
from pydantic import ValidationError
from app.models.schemas import VideoUrlRequests


# ============================================================================
# 정상 케이스 테스트
# ============================================================================

def test_video_url_request_success(sample_youtube_url):
    """정상적인 YouTube URL 입력 테스트"""
    # Arrange (준비): fixture에서 정상 URL 가져오기
    # Act (실행): VideoUrlRequest 객체 생성
    data = VideoUrlRequests(url=sample_youtube_url)
    
    # Assert (검증): 결과 확인
    assert data.url == sample_youtube_url
    print(f"\n✅ 정상 케이스 테스트 성공!")
    print(f"입력 URL: {sample_youtube_url}")
    print(f"객체 URL: {data.url}")


def test_video_url_request_multiple_valid_urls():
    """여러 정상 URL 테스트"""
    test_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://www.youtube.com/watch?v=1234567890",
        "https://www.youtube.com/watch?v=abcDEF123",
    ]
    
    print(f"\n✅ 여러 정상 URL 테스트:")
    for url in test_urls:
        data = VideoUrlRequests(url=url)
        assert data.url == url
        print(f"  - {url} ✓")


# ============================================================================
# 필드 없음 테스트
# ============================================================================

def test_video_url_request_missing_url():
    """url 필드가 없을 때 에러 발생 테스트"""
    # Arrange & Act & Assert: url 필드 없이 생성 시도하면 ValidationError 발생해야 함
    with pytest.raises(ValidationError) as exc_info:
        VideoUrlRequests()
    
    # 에러 메시지 확인
    errors = exc_info.value.errors()
    assert len(errors) > 0
    assert errors[0]["type"] == "missing"
    assert errors[0]["loc"] == ("url",)
    
    print(f"\n✅ 에러 케이스 테스트 성공!")
    print(f"에러 타입: {errors[0]['type']}")
    print(f"에러 필드: {errors[0]['loc']}")


# ============================================================================
# 빈 값 검증 테스트 (validate_url_not_empty)
# ============================================================================

def test_video_url_request_empty_string(empty_string):
    """빈 문자열 입력 시 에러 발생 테스트"""
    # Arrange (준비): fixture에서 빈 문자열 가져오기
    # Act & Assert: 빈 문자열로 생성 시도하면 ValidationError 발생해야 함
    with pytest.raises(ValidationError) as exc_info:
        VideoUrlRequests(url=empty_string)
    
    # 에러 메시지 확인
    errors = exc_info.value.errors()
    assert len(errors) > 0
    assert errors[0]["type"] == "value_error"
    
    # 에러 메시지에 "비어있을 수 없습니다" 포함 확인
    error_msg = str(errors[0]["msg"])
    assert "비어있을 수 없습니다" in error_msg
    
    print(f"\n✅ 빈 문자열 테스트 성공!")
    print(f"에러 메시지: {error_msg}")


def test_video_url_request_whitespace_only(whitespace_only):
    """공백만 있는 문자열 입력 시 에러 발생 테스트"""
    # Arrange (준비): fixture에서 공백만 있는 문자열 가져오기
    # Act & Assert: 공백만으로 생성 시도하면 ValidationError 발생해야 함
    with pytest.raises(ValidationError) as exc_info:
        VideoUrlRequests(url=whitespace_only)
    
    # 에러 메시지 확인
    errors = exc_info.value.errors()
    assert len(errors) > 0
    assert errors[0]["type"] == "value_error"
    
    error_msg = str(errors[0]["msg"])
    assert "비어있을 수 없습니다" in error_msg
    
    print(f"\n✅ 공백만 있는 문자열 테스트 성공!")
    print(f"에러 메시지: {error_msg}")


# ============================================================================
# URL 형식 검증 테스트 (validate_url_format)
# ============================================================================

def test_video_url_request_invalid_url_format_text(invalid_url_format_text):
    """텍스트만 입력 시 에러 발생 테스트"""
    # Arrange (준비): fixture에서 텍스트만 가져오기
    # Act & Assert: 텍스트만으로 생성 시도하면 ValidationError 발생해야 함
    with pytest.raises(ValidationError) as exc_info:
        VideoUrlRequests(url=invalid_url_format_text)
    
    # 에러 메시지 확인
    errors = exc_info.value.errors()
    assert len(errors) > 0
    assert errors[0]["type"] == "value_error"
    
    error_msg = str(errors[0]["msg"])
    assert "형식이 올바르지 않습니다" in error_msg or "비어있을 수 없습니다" in error_msg
    
    print(f"\n✅ 텍스트만 입력 테스트 성공!")
    print(f"에러 메시지: {error_msg}")


def test_video_url_request_invalid_url_format_no_scheme(invalid_url_format_no_scheme):
    """scheme 없는 URL 입력 시 에러 발생 테스트"""
    # Arrange (준비): fixture에서 scheme 없는 URL 가져오기
    # Act & Assert: scheme 없는 URL로 생성 시도하면 ValidationError 발생해야 함
    with pytest.raises(ValidationError) as exc_info:
        VideoUrlRequests(url=invalid_url_format_no_scheme)
    
    # 에러 메시지 확인
    errors = exc_info.value.errors()
    assert len(errors) > 0
    assert errors[0]["type"] == "value_error"
    
    error_msg = str(errors[0]["msg"])
    assert "형식이 올바르지 않습니다" in error_msg
    
    print(f"\n✅ scheme 없는 URL 테스트 성공!")
    print(f"에러 메시지: {error_msg}")


# ============================================================================
# YouTube URL 형식 검증 테스트 (validate_youtube_url)
# ============================================================================

def test_video_url_request_non_youtube_url(invalid_url):
    """YouTube가 아닌 URL 입력 시 에러 발생 테스트"""
    # Arrange (준비): fixture에서 YouTube가 아닌 URL 가져오기
    # Act & Assert: YouTube가 아닌 URL로 생성 시도하면 ValidationError 발생해야 함
    with pytest.raises(ValidationError) as exc_info:
        VideoUrlRequests(url=invalid_url)
    
    # 에러 메시지 확인
    errors = exc_info.value.errors()
    assert len(errors) > 0
    assert errors[0]["type"] == "value_error"
    
    error_msg = str(errors[0]["msg"])
    assert "YouTube URL" in error_msg or "형식이 올바르지 않습니다" in error_msg
    
    print(f"\n✅ YouTube가 아닌 URL 테스트 성공!")
    print(f"에러 메시지: {error_msg}")


def test_video_url_request_youtube_short_url(sample_youtube_short_url):
    """youtu.be 형식 URL 입력 시 에러 발생 테스트"""
    # Arrange (준비): fixture에서 youtu.be 형식 URL 가져오기
    # Act & Assert: youtu.be 형식으로 생성 시도하면 ValidationError 발생해야 함
    with pytest.raises(ValidationError) as exc_info:
        VideoUrlRequests(url=sample_youtube_short_url)
    
    # 에러 메시지 확인
    errors = exc_info.value.errors()
    assert len(errors) > 0
    assert errors[0]["type"] == "value_error"
    
    error_msg = str(errors[0]["msg"])
    assert "YouTube URL" in error_msg or "형식이 올바르지 않습니다" in error_msg
    
    print(f"\n✅ youtu.be 형식 URL 테스트 성공!")
    print(f"에러 메시지: {error_msg}")


def test_video_url_request_youtube_without_www(youtube_url_without_www):
    """www 없이 youtube.com 형식 URL 입력 시 에러 발생 테스트"""
    # Arrange (준비): fixture에서 www 없는 YouTube URL 가져오기
    # Act & Assert: www 없는 URL로 생성 시도하면 ValidationError 발생해야 함
    with pytest.raises(ValidationError) as exc_info:
        VideoUrlRequests(url=youtube_url_without_www)
    
    # 에러 메시지 확인
    errors = exc_info.value.errors()
    assert len(errors) > 0
    assert errors[0]["type"] == "value_error"
    
    error_msg = str(errors[0]["msg"])
    assert "YouTube URL" in error_msg or "형식이 올바르지 않습니다" in error_msg
    
    print(f"\n✅ www 없는 YouTube URL 테스트 성공!")
    print(f"에러 메시지: {error_msg}")


def test_video_url_request_youtube_wrong_path(youtube_url_wrong_path):
    """잘못된 경로(/embed)를 가진 YouTube URL 입력 시 에러 발생 테스트"""
    # Arrange (준비): fixture에서 잘못된 경로 URL 가져오기
    # Act & Assert: 잘못된 경로 URL로 생성 시도하면 ValidationError 발생해야 함
    with pytest.raises(ValidationError) as exc_info:
        VideoUrlRequests(url=youtube_url_wrong_path)
    
    # 에러 메시지 확인
    errors = exc_info.value.errors()
    assert len(errors) > 0
    assert errors[0]["type"] == "value_error"
    
    error_msg = str(errors[0]["msg"])
    assert "YouTube URL" in error_msg or "형식이 올바르지 않습니다" in error_msg
    
    print(f"\n✅ 잘못된 경로 YouTube URL 테스트 성공!")
    print(f"에러 메시지: {error_msg}")


def test_video_url_request_youtube_no_v_param(youtube_url_no_v_param):
    """v 파라미터가 없는 YouTube URL 입력 시 에러 발생 테스트"""
    # Arrange (준비): fixture에서 v 파라미터 없는 URL 가져오기
    # Act & Assert: v 파라미터 없는 URL로 생성 시도하면 ValidationError 발생해야 함
    with pytest.raises(ValidationError) as exc_info:
        VideoUrlRequests(url=youtube_url_no_v_param)
    
    # 에러 메시지 확인
    errors = exc_info.value.errors()
    assert len(errors) > 0
    assert errors[0]["type"] == "value_error"
    
    error_msg = str(errors[0]["msg"])
    assert "YouTube URL" in error_msg or "형식이 올바르지 않습니다" in error_msg
    
    print(f"\n✅ v 파라미터 없는 YouTube URL 테스트 성공!")
    print(f"에러 메시지: {error_msg}")
