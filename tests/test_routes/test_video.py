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


# ============================================================================
# POST /api/video/{video_id}/transcript 엔드포인트 테스트
# ============================================================================

def test_post_get_video_transcript_success(
    running_server_client: httpx.Client, 
    sample_video_id
):
    """정상적인 Video ID로 자막 추출 요청 시 성공 응답 테스트
    
    테스트 대상:
        - app/routes/video.py의 POST /api/video/{video_id}/transcript 엔드포인트
        - 자막이 있는 영상으로 자막 추출 성공 확인
    """
    # Arrange (준비): fixture에서 정상 Video ID 가져오기
    video_id = sample_video_id
    
    # Act (실행): POST 요청 보내기
    response = running_server_client.post(
        f"/api/video/{video_id}/transcript",
        follow_redirects=True
    )
    
    # Assert (검증): 응답 확인
    print(f"\n[테스트 결과] POST /api/video/{video_id}/transcript (정상 케이스)")
    print(f"Video ID: {video_id}")
    print(f"상태 코드: {response.status_code}")
    
    # 응답이 JSON인지 확인
    if response.headers.get("content-type", "").startswith("application/json"):
        data = response.json()
        print(f"응답 내용 (일부): {str(data)[:200]}...")
    else:
        print(f"응답 내용: {response.text}")
        raise AssertionError(f"예상하지 못한 응답 형식: {response.headers.get('content-type')}")
    
    assert response.status_code == 200
    assert "video_id" in data
    assert "transcript" in data
    assert "status" in data
    assert "language" in data
    assert data["status"] == "success"
    assert data["video_id"] == video_id
    assert data["language"] == "en"
    assert len(data["transcript"]) > 0  # 자막 리스트가 비어있지 않은지 확인
    assert isinstance(data["transcript"], list)  # transcript가 리스트인지 확인
    
    # 각 청크가 딕셔너리이고 필요한 키를 가지고 있는지 확인
    for chunk in data["transcript"]:
        assert isinstance(chunk, dict), f"청크가 딕셔너리가 아닙니다: {type(chunk)}"
        assert "text" in chunk, "청크에 'text' 키가 없습니다"
        assert "token_count" in chunk, "청크에 'token_count' 키가 없습니다"
        assert "segment_range" in chunk, "청크에 'segment_range' 키가 없습니다"
        assert isinstance(chunk["text"], str), "'text'가 문자열이 아닙니다"
        assert isinstance(chunk["token_count"], int), "'token_count'가 정수가 아닙니다"
        assert isinstance(chunk["segment_range"], str), "'segment_range'가 문자열이 아닙니다"
    
    print("✅ 정상 케이스 테스트 성공!")


def test_post_get_video_transcript_invalid_video_id(
    running_server_client: httpx.Client,
    invalid_video_id
):
    """존재하지 않는 Video ID로 자막 추출 요청 시 에러 응답 테스트
    
    테스트 대상:
        - app/routes/video.py의 POST /api/video/{video_id}/transcript 엔드포인트
        - app/services/transcript.py의 get_transcript 함수
        - 존재하지 않는 영상 ID 입력 시 400 에러 반환 확인
    """
    # Arrange (준비): fixture에서 존재하지 않는 Video ID 가져오기
    video_id = invalid_video_id
    
    # Act (실행): POST 요청 보내기
    response = running_server_client.post(
        f"/api/video/{video_id}/transcript",
        follow_redirects=True
    )
    
    # Assert (검증): 400 에러 확인
    print(f"\n[테스트 결과] POST /api/video/{video_id}/transcript (존재하지 않는 Video ID)")
    print(f"Video ID: {video_id}")
    print(f"상태 코드: {response.status_code}")
    
    # 응답이 JSON인지 확인
    if response.headers.get("content-type", "").startswith("application/json"):
        error_data = response.json()
        print(f"응답 내용: {error_data}")
    else:
        print(f"응답 내용: {response.text}")
        raise AssertionError(f"예상하지 못한 응답 형식: {response.headers.get('content-type')}")
    
    assert response.status_code == 400
    assert "detail" in error_data
    # 에러 메시지가 사용자 친화적으로 변경되었으므로 Video ID 포함 여부는 확인하지 않음
    print("✅ 존재하지 않는 Video ID 테스트 성공! (400 에러 정상)")


# ============================================================================
# POST /api/video/{video_id}/vocabulary 엔드포인트 테스트
# ============================================================================

def test_post_generate_vocabulary_success(
    skip_if_server_unavailable,
    running_server_client: httpx.Client,
    sample_video_id
):
    """정상적인 Video ID로 단어장 생성 요청 시 성공 응답 테스트
    
    테스트 대상:
        - app/routes/video.py의 POST /api/video/{video_id}/vocabulary 엔드포인트
        - 자막이 있는 영상으로 단어장 생성 성공 확인
        
    주의사항:
        - 이 테스트는 LLM 처리가 필요하므로 시간이 오래 걸릴 수 있습니다 (수십 초 ~ 수분)
        - vLLM 서버가 실행 중이어야 합니다
        - 서버가 실행 중이지 않으면 자동으로 스킵됩니다
    """
    # Arrange (준비): fixture에서 정상 Video ID 가져오기
    video_id = sample_video_id
    
    # Act (실행): POST 요청 보내기 (LLM 처리가 필요하므로 타임아웃을 길게 설정)
    print(f"\n[테스트 시작] POST /api/video/{video_id}/vocabulary (정상 케이스)")
    print(f"⚠️  이 테스트는 LLM 처리가 필요하므로 시간이 오래 걸릴 수 있습니다...")
    print(f"Video ID: {video_id}")
    
    try:
        response = running_server_client.post(
            f"/api/video/{video_id}/vocabulary",
            follow_redirects=True,
            timeout=300.0  # 5분 타임아웃 (LLM 처리 시간 고려)
        )
    except httpx.TimeoutException:
        print("❌ 요청 타임아웃 (5분 초과)")
        pytest.fail("단어장 생성 요청이 타임아웃되었습니다. vLLM 서버 상태를 확인해주세요.")
    
    # Assert (검증): 응답 확인
    print(f"상태 코드: {response.status_code}")
    
    # 응답이 JSON인지 확인
    if response.headers.get("content-type", "").startswith("application/json"):
        data = response.json()
        print(f"응답 내용 (일부): video_id={data.get('video_id')}, words={len(data.get('words', []))}, phrases={len(data.get('phrases', []))}")
    else:
        print(f"응답 내용: {response.text[:500]}")
        raise AssertionError(f"예상하지 못한 응답 형식: {response.headers.get('content-type')}")
    
    assert response.status_code == 200
    assert "video_id" in data
    assert "words" in data
    assert "phrases" in data
    assert "status" in data
    assert data["status"] == "success"
    assert data["video_id"] == video_id
    assert isinstance(data["words"], list)
    assert isinstance(data["phrases"], list)
    
    # 단어 엔트리 구조 검증
    if len(data["words"]) > 0:
        word_entry = data["words"][0]
        assert "word" in word_entry
        assert "pos" in word_entry
        assert "meanings" in word_entry
        assert "synonyms" in word_entry
        assert "example" in word_entry
        assert isinstance(word_entry["meanings"], list)
        assert isinstance(word_entry["synonyms"], list)
        assert isinstance(word_entry["example"], str)
    
    # 숙어 엔트리 구조 검증
    if len(data["phrases"]) > 0:
        phrase_entry = data["phrases"][0]
        assert "phrase" in phrase_entry
        assert "meaning" in phrase_entry
        assert "example" in phrase_entry
        assert isinstance(phrase_entry["meaning"], str)
        assert isinstance(phrase_entry["example"], str)
    
    print(f"✅ 정상 케이스 테스트 성공! (단어: {len(data['words'])}개, 숙어: {len(data['phrases'])}개)")


def test_post_generate_vocabulary_invalid_video_id(
    skip_if_server_unavailable,
    running_server_client: httpx.Client,
    invalid_video_id
):
    """존재하지 않는 Video ID로 단어장 생성 요청 시 에러 응답 테스트
    
    테스트 대상:
        - app/routes/video.py의 POST /api/video/{video_id}/vocabulary 엔드포인트
        - 존재하지 않는 영상 ID 입력 시 400 에러 반환 확인
    """
    # Arrange (준비): fixture에서 존재하지 않는 Video ID 가져오기
    video_id = invalid_video_id
    
    # Act (실행): POST 요청 보내기
    print(f"\n[테스트 결과] POST /api/video/{video_id}/vocabulary (존재하지 않는 Video ID)")
    print(f"Video ID: {video_id}")
    
    response = running_server_client.post(
        f"/api/video/{video_id}/vocabulary",
        follow_redirects=True,
        timeout=30.0  # 에러 케이스는 빠르게 처리될 것으로 예상
    )
    
    # Assert (검증): 400 에러 확인
    print(f"상태 코드: {response.status_code}")
    
    # 응답이 JSON인지 확인
    if response.headers.get("content-type", "").startswith("application/json"):
        error_data = response.json()
        print(f"응답 내용: {error_data}")
    else:
        print(f"응답 내용: {response.text}")
        raise AssertionError(f"예상하지 못한 응답 형식: {response.headers.get('content-type')}")
    
    assert response.status_code == 400
    assert "detail" in error_data
    # 에러 메시지가 사용자 친화적으로 변경되었으므로 Video ID 포함 여부는 확인하지 않음
    print("✅ 존재하지 않는 Video ID 테스트 성공! (400 에러 정상)")

