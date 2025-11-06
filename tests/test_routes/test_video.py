"""
비디오 라우트 엔드포인트 테스트

이 테스트는 실행 중인 서버를 대상으로 합니다.
사용법:
    1. 터미널에서 서버 실행: uvicorn app.main:app --reload
    2. 다른 터미널에서 테스트 실행: pytest tests/test_routes/test_video.py -v -s
"""
import pytest
import httpx

# pytest fixture는 conftest.py에서 자동으로 사용 가능
# fixture 이름을 함수 매개변수로 사용하면 자동으로 주입됨


# ============================================================================
# 정상 케이스 테스트
# ============================================================================

def test_post_video_success(running_server_client: httpx.Client, sample_youtube_url):
    """정상적인 YouTube URL로 POST 요청 시 성공 응답 테스트
    
    테스트 대상:
        - app/routes/video.py의 POST /api/video 엔드포인트
        - 정상적인 YouTube URL 입력 시 Video ID 반환 확인
    """
    # Arrange (준비): fixture에서 정상 URL 가져오기
    url = sample_youtube_url
    
    # Act (실행): POST 요청 보내기 (리다이렉트 자동 추적)
    response = running_server_client.post(
        "/api/video",
        json={"url": url},
        follow_redirects=True
    )
    
    # Assert (검증): 응답 확인
    print(f"\n[테스트 결과] POST /api/video (정상 케이스)")
    print(f"요청 URL: {url}")
    print(f"상태 코드: {response.status_code}")
    
    # 응답이 JSON인지 확인
    if response.headers.get("content-type", "").startswith("application/json"):
        data = response.json()
        print(f"응답 내용: {data}")
    else:
        print(f"응답 내용: {response.text}")
        raise AssertionError(f"예상하지 못한 응답 형식: {response.headers.get('content-type')}")
    
    assert response.status_code == 200
    assert "video_id" in data
    assert "status" in data
    assert data["status"] == "success"
    assert data["video_id"] == "dQw4w9WgXcQ"  # fixture에서 사용한 Video ID
    print("✅ 정상 케이스 테스트 성공!")


# ============================================================================
# 스키마 검증 실패 테스트 (422 Unprocessable Entity)
# ============================================================================

def test_post_video_empty_url(running_server_client: httpx.Client, empty_string):
    """빈 URL로 POST 요청 시 422 에러 테스트
    
    테스트 대상:
        - app/models/schemas.py의 validate_url_not_empty 검증
        - 스키마 검증 실패 시 422 에러 반환 확인
    """
    # Arrange (준비): fixture에서 빈 문자열 가져오기
    url = empty_string
    
    # Act (실행): POST 요청 보내기 (리다이렉트 자동 추적)
    response = running_server_client.post(
        "/api/video",
        json={"url": url},
        follow_redirects=True
    )
    
    # Assert (검증): 422 에러 확인
    print(f"\n[테스트 결과] POST /api/video (빈 URL)")
    print(f"요청 URL: '{url}'")
    print(f"상태 코드: {response.status_code}")
    
    # 응답이 JSON인지 확인
    if response.headers.get("content-type", "").startswith("application/json"):
        error_data = response.json()
        print(f"응답 내용: {error_data}")
    else:
        print(f"응답 내용: {response.text}")
        raise AssertionError(f"예상하지 못한 응답 형식: {response.headers.get('content-type')}")
    
    assert response.status_code == 422
    assert "detail" in error_data
    print("✅ 빈 URL 테스트 성공! (422 에러 정상)")


def test_post_video_invalid_url_format_text(
    running_server_client: httpx.Client, 
    invalid_url_format_text
):
    """텍스트만 있는 URL로 POST 요청 시 422 에러 테스트
    
    테스트 대상:
        - app/models/schemas.py의 validate_url_format 검증
        - 잘못된 URL 형식 시 422 에러 반환 확인
    """
    # Arrange (준비): fixture에서 잘못된 형식 URL 가져오기
    url = invalid_url_format_text
    
    # Act (실행): POST 요청 보내기 (리다이렉트 자동 추적)
    response = running_server_client.post(
        "/api/video",
        json={"url": url},
        follow_redirects=True
    )
    
    # Assert (검증): 422 에러 확인
    print(f"\n[테스트 결과] POST /api/video (잘못된 URL 형식)")
    print(f"요청 URL: {url}")
    print(f"상태 코드: {response.status_code}")
    
    # 응답이 JSON인지 확인
    if response.headers.get("content-type", "").startswith("application/json"):
        print(f"응답 내용: {response.json()}")
        error_data = response.json()
    else:
        print(f"응답 내용: {response.text}")
        raise AssertionError(f"예상하지 못한 응답 형식: {response.headers.get('content-type')}")
    
    assert response.status_code == 422
    assert "detail" in error_data
    print("✅ 잘못된 URL 형식 테스트 성공! (422 에러 정상)")


def test_post_video_invalid_url_format_no_scheme(
    running_server_client: httpx.Client,
    invalid_url_format_no_scheme
):
    """scheme 없는 URL로 POST 요청 시 422 에러 테스트
    
    테스트 대상:
        - app/models/schemas.py의 validate_url_format 검증
        - scheme 없는 URL 시 422 에러 반환 확인
    """
    # Arrange (준비): fixture에서 scheme 없는 URL 가져오기
    url = invalid_url_format_no_scheme
    
    # Act (실행): POST 요청 보내기 (리다이렉트 자동 추적)
    response = running_server_client.post(
        "/api/video",
        json={"url": url},
        follow_redirects=True
    )
    
    # Assert (검증): 422 에러 확인
    print(f"\n[테스트 결과] POST /api/video (scheme 없는 URL)")
    print(f"요청 URL: {url}")
    print(f"상태 코드: {response.status_code}")
    
    # 응답이 JSON인지 확인
    if response.headers.get("content-type", "").startswith("application/json"):
        print(f"응답 내용: {response.json()}")
        error_data = response.json()
    else:
        print(f"응답 내용: {response.text}")
        raise AssertionError(f"예상하지 못한 응답 형식: {response.headers.get('content-type')}")
    
    assert response.status_code == 422
    assert "detail" in error_data
    print("✅ scheme 없는 URL 테스트 성공! (422 에러 정상)")


def test_post_video_no_video_id(running_server_client: httpx.Client):
    """Video ID가 없는 URL로 POST 요청 시 422 에러 테스트
    
    테스트 대상:
        - app/models/schemas.py의 validate_youtube_url 검증
        - Video ID 없는 URL 시 422 에러 반환 확인
    """
    # Arrange (준비): Video ID 없는 URL
    url = "https://www.youtube.com/watch?v="
    
    # Act (실행): POST 요청 보내기 (리다이렉트 자동 추적)
    response = running_server_client.post(
        "/api/video",
        json={"url": url},
        follow_redirects=True
    )
    
    # Assert (검증): 422 에러 확인
    print(f"\n[테스트 결과] POST /api/video (Video ID 없음)")
    print(f"요청 URL: {url}")
    print(f"상태 코드: {response.status_code}")
    
    # 응답이 JSON인지 확인
    if response.headers.get("content-type", "").startswith("application/json"):
        print(f"응답 내용: {response.json()}")
        error_data = response.json()
    else:
        print(f"응답 내용: {response.text}")
        raise AssertionError(f"예상하지 못한 응답 형식: {response.headers.get('content-type')}")
    
    assert response.status_code == 422
    assert "detail" in error_data
    print("✅ Video ID 없는 URL 테스트 성공! (422 에러 정상)")


def test_post_video_non_youtube_url(running_server_client: httpx.Client):
    """YouTube가 아닌 URL로 POST 요청 시 422 에러 테스트
    
    테스트 대상:
        - app/models/schemas.py의 validate_youtube_url 검증
        - YouTube가 아닌 URL 시 422 에러 반환 확인
    """
    # Arrange (준비): YouTube가 아닌 URL
    url = "https://google.com"
    
    # Act (실행): POST 요청 보내기 (리다이렉트 자동 추적)
    response = running_server_client.post(
        "/api/video",
        json={"url": url},
        follow_redirects=True
    )
    
    # Assert (검증): 422 에러 확인
    print(f"\n[테스트 결과] POST /api/video (YouTube가 아닌 URL)")
    print(f"요청 URL: {url}")
    print(f"상태 코드: {response.status_code}")
    
    # 응답이 JSON인지 확인
    if response.headers.get("content-type", "").startswith("application/json"):
        print(f"응답 내용: {response.json()}")
        error_data = response.json()
    else:
        print(f"응답 내용: {response.text}")
        raise AssertionError(f"예상하지 못한 응답 형식: {response.headers.get('content-type')}")
    
    assert response.status_code == 422
    assert "detail" in error_data
    print("✅ YouTube가 아닌 URL 테스트 성공! (422 에러 정상)")

