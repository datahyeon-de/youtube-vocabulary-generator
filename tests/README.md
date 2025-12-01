# FastAPI 테스트 가이드

FastAPI 프로젝트에서 `tests/` 폴더를 활용하는 완벽한 가이드입니다. 이 문서는 테스트를 처음 작성하는 개발자도 쉽게 따라할 수 있도록 상세하게 작성되었습니다.

---

## 📋 목차

1. [테스트 폴더 구조](#📁-테스트-폴더-구조)
2. [테스트 종류 및 파일 분류](#🧪-테스트-종류-및-파일-분류)
3. [테스트 파일 상세 설명](#📝-테스트-파일-상세-설명)
4. [conftest.py 설정 파일 설명](#⚙️-conftestpy-설정-파일-설명)
5. [테스트 실행 방법](#🚀-테스트-실행-방법)
6. [테스트 실행 옵션 및 결과 해석](#📊-테스트-실행-옵션-및-결과-해석)
7. [테스트 모듈 작성 가이드](#📖-테스트-모듈-작성-가이드)
8. [테스트 디버깅 가이드](#8-테스트-디버깅-가이드)
9. [테스트 작성 시 주의사항](#9-테스트-작성-시-주의사항)
10. [테스트 모범 사례](#10-테스트-모범-사례)
11. [테스트 실행 체크리스트](#11-테스트-실행-체크리스트)
12. [문제 해결 FAQ](#12-문제-해결-faq)
13. [참고 자료](#🔗-참고-자료)

---

## 📁 테스트 폴더 구조

```
tests/
├── __init__.py                    # Python 패키지 초기화 파일
├── conftest.py                    # 전체 공통 fixture 및 설정
├── README.md                      # 이 문서
├── test_main.py                   # FastAPI 앱 메인 테스트
│
├── test_models/                   # 모델/스키마 테스트
│   ├── __init__.py
│   ├── conftest.py                # 모델 테스트 전용 fixture
│   └── test_schemas.py            # Pydantic 스키마 검증 테스트
│
├── test_routes/                   # 라우트/엔드포인트 테스트
│   ├── __init__.py
│   ├── conftest.py                # 라우트 테스트 전용 fixture
│   └── test_video.py              # 비디오 관련 API 엔드포인트 테스트
│
└── test_services/                 # 서비스 로직 테스트
    ├── __init__.py
    ├── conftest.py                # LLM 서비스 테스트 전용 fixture (vLLM 서버 확인)
    ├── test_llm_prompts.py        # LLM 프롬프트 규칙 테스트
    ├── test_llm_extract_words.py  # 단어 추출 모듈 테스트 (1단계)
    ├── test_llm_extract_phrases.py # 숙어 추출 모듈 테스트 (1단계)
    ├── test_llm_enrich_words.py   # 단어 상세 정보 생성 모듈 테스트 (2단계)
    ├── test_llm_enrich_phrases.py # 숙어 예문 생성 모듈 테스트 (2단계)
    ├── test_llm_prompt_ab_test.py # 프롬프트 A/B 테스트 (1단계, 2단계 통합)
    ├── test_llm_prompt_ab_test_prompts.py # A/B 테스트용 프롬프트 함수들 (40개 버전)
    ├── ab_test_results/           # A/B 테스트 결과 저장 디렉토리
    ├── test_validator.py          # 링크 검증 서비스 테스트 (향후)
    └── test_transcript.py         # 자막 추출 서비스 테스트 (향후)
```

### 폴더 구조 설명

- **`tests/`**: 모든 테스트 파일의 루트 디렉토리
- **`test_models/`**: Pydantic 스키마 및 데이터 모델 테스트
- **`test_routes/`**: FastAPI 엔드포인트 및 HTTP 요청/응답 테스트
- **`test_services/`**: 비즈니스 로직 및 서비스 함수 테스트
- **`conftest.py`**: 각 폴더별 공통 fixture 정의 (pytest가 자동으로 인식)

---

**[↑ 목차로 돌아가기](#📋-목차)**

---

## 🧪 테스트 종류 및 파일 분류

이 프로젝트에서는 **3가지 테스트 종류**를 사용합니다. 각 테스트 종류는 목적과 테스트 방법이 다르므로 올바른 종류를 선택하는 것이 중요합니다.

### 1. 단위 테스트 (Unit Tests)

**목적**: 개별 함수나 메서드의 동작을 독립적으로 테스트

**특징**:
- 외부 의존성 제거 (Mock 사용)
- 빠른 실행 속도
- 격리된 환경에서 테스트

**해당 파일**:
- `test_models/test_schemas.py` - Pydantic 스키마 검증 로직 테스트
- `test_services/test_llm_prompts.py` - 단어/숙어 추출 프롬프트 규칙 테스트
- `test_services/test_llm_extract_words.py` - 단어 추출 함수 테스트 (1단계)
- `test_services/test_llm_extract_phrases.py` - 숙어 추출 함수 테스트 (1단계)
- `test_services/test_llm_enrich_words.py` - 단어 상세 정보 생성 함수 테스트 (2단계)
- `test_services/test_llm_enrich_phrases.py` - 숙어 예문 생성 함수 테스트 (2단계)
- `test_services/test_llm_prompt_ab_test.py` - 프롬프트 A/B 테스트 (1단계, 2단계 통합 테스트)
- `test_services/test_validator.py` (향후) - URL 검증 함수 테스트
- `test_services/test_transcript.py` (향후) - 자막 추출 함수 테스트

**예시**:
```python
# 스키마 검증 함수를 직접 호출하여 테스트
def test_validate_url_success():
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    result = validate_youtube_url(url)
    assert result == True
```

---

### 2. 통합 테스트 (Integration Tests)

**목적**: 여러 컴포넌트가 함께 작동하는지 테스트

**특징**:
- 실제 외부 API 호출 가능 (또는 Mock)
- 여러 레이어 간 상호작용 검증
- 단위 테스트보다 느리지만 실제 동작에 가까움

**해당 파일**:
- `test_services/test_transcript.py` (향후) - YouTube Transcript API 연동 테스트

**예시**:
```python
# 실제 YouTube API를 호출하여 자막 추출 테스트
def test_get_transcript_integration():
    video_id = "dQw4w9WgXcQ"
    transcript = get_transcript(video_id)
    assert len(transcript) > 0
```

---

### 3. API 테스트 (E2E Tests - End-to-End Tests)

**목적**: FastAPI 엔드포인트 전체 플로우를 실제 HTTP 요청으로 테스트

**특징**:
- 실제 HTTP 요청/응답 테스트
- 전체 스택 검증 (라우터 → 서비스 → 응답)
- 실행 중인 서버 필요 (또는 TestClient 사용)

**해당 파일**:
- `test_main.py` - FastAPI 앱 메인 테스트
- `test_routes/test_video.py` - 비디오 관련 API 엔드포인트 테스트

**예시**:
```python
# 실제 HTTP 요청으로 엔드포인트 테스트
def test_post_video_success(running_server_client):
    response = running_server_client.post(
        "/api/video",
        json={"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}
    )
    assert response.status_code == 200
```

---

**[↑ 목차로 돌아가기](#📋-목차)**

---

## 📝 테스트 파일 상세 설명

각 테스트 파일의 목적, 테스트 대상, 주요 테스트 모듈을 상세히 설명합니다.

### `test_main.py` - FastAPI 앱 메인 테스트

**파일 경로**: `tests/test_main.py`

**목적**: FastAPI 애플리케이션의 기본 동작을 테스트합니다.

**테스트 대상**:
- `app/main.py`의 FastAPI 앱 인스턴스
- 루트 엔드포인트 (`GET /`)
- Health check 엔드포인트 (`GET /health`)

**주요 테스트 모듈**:

1. **`test_app_startup(client)`**
   - **목적**: 앱이 정상적으로 시작되는지 확인
   - **테스트 방법**: TestClient를 사용한 인메모리 테스트
   - **검증**: 루트 엔드포인트 응답 확인

2. **`test_health_check(client)`**
   - **목적**: Health check 엔드포인트 동작 확인
   - **테스트 방법**: TestClient를 사용한 인메모리 테스트
   - **검증**: Health check 응답 형식 확인

3. **`test_root_endpoint_running_server(running_server_client)`**
   - **목적**: 실행 중인 서버의 루트 엔드포인트 테스트
   - **테스트 방법**: 실제 실행 중인 서버에 HTTP 요청
   - **검증**: 네트워크 레벨의 통합 테스트

4. **`test_health_check_running_server(running_server_client)`**
   - **목적**: 실행 중인 서버의 health check 테스트
   - **테스트 방법**: 실제 실행 중인 서버에 HTTP 요청
   - **검증**: 서버 상태 확인

5. **`test_multiple_requests_running_server(running_server_client)`**
   - **목적**: 여러 요청을 연속으로 보내는 테스트
   - **테스트 방법**: 실제 실행 중인 서버에 여러 HTTP 요청
   - **검증**: 서버의 안정성 및 연속 요청 처리 확인

---

### `test_models/test_schemas.py` - Pydantic 스키마 테스트

**파일 경로**: `tests/test_models/test_schemas.py`

**목적**: Pydantic 스키마의 검증 로직을 테스트합니다.

**테스트 대상**:
- `app/models/schemas.py`의 `VideoUrlRequests` 스키마
- URL 검증 로직 (`validate_url_not_empty`, `validate_url_format`, `validate_youtube_url`)
- `VideoUrlResponse` 스키마

**주요 테스트 모듈**:

1. **정상 케이스 테스트**
   - `test_video_url_request_success`: 정상적인 YouTube URL 입력 테스트
   - `test_video_url_request_multiple_valid_urls`: 여러 정상 URL 테스트

2. **필드 검증 테스트**
   - `test_video_url_request_missing_url`: 필수 필드 누락 시 에러 발생 확인

3. **빈 값 검증 테스트**
   - `test_video_url_request_empty_string`: 빈 문자열 입력 시 에러 발생 확인
   - `test_video_url_request_whitespace_only`: 공백만 있는 문자열 입력 시 에러 발생 확인

4. **URL 형식 검증 테스트**
   - `test_video_url_request_invalid_url_format_text`: 텍스트만 입력 시 에러 발생 확인
   - `test_video_url_request_invalid_url_format_no_scheme`: scheme 없는 URL 입력 시 에러 발생 확인

5. **YouTube URL 형식 검증 테스트**
   - `test_video_url_request_non_youtube_url`: YouTube가 아닌 URL 입력 시 에러 발생 확인
   - `test_video_url_request_youtube_short_url`: youtu.be 형식 URL 입력 시 에러 발생 확인
   - `test_video_url_request_youtube_without_www`: www 없이 youtube.com 형식 URL 입력 시 에러 발생 확인
   - `test_video_url_request_youtube_wrong_path`: 잘못된 경로(/embed)를 가진 YouTube URL 입력 시 에러 발생 확인
   - `test_video_url_request_youtube_no_v_param`: v 파라미터가 없는 YouTube URL 입력 시 에러 발생 확인

**테스트 방법**: Pydantic의 `ValidationError`를 사용하여 검증 실패 시 예외 발생을 확인합니다.

---

### `test_routes/test_video.py` - 비디오 관련 API 엔드포인트 테스트

**파일 경로**: `tests/test_routes/test_video.py`

**목적**: 비디오 관련 FastAPI 엔드포인트를 실제 HTTP 요청으로 테스트합니다.

**중요**: 이 테스트는 **실행 중인 서버**를 대상으로 합니다. 테스트 실행 전에 서버를 먼저 실행해야 합니다.

**테스트 대상**:
- `app/routes/video.py`의 모든 엔드포인트
- `POST /api/video` - YouTube URL 처리 및 Video ID 반환
- `POST /api/video/{video_id}/transcript` - Video ID로 자막 추출
- `POST /api/video/{video_id}/vocabulary` - Video ID로 단어장 생성

**주요 테스트 모듈**:

#### POST /api/video 엔드포인트 테스트

1. **`test_post_video_success`**
   - **목적**: 정상적인 YouTube URL로 POST 요청 시 성공 응답 확인
   - **테스트 방법**: 실행 중인 서버에 HTTP POST 요청
   - **검증**: 
     - 상태 코드 200
     - 응답에 `video_id`, `status` 포함
     - `status`가 "success"
     - `video_id`가 올바른 값

2. **`test_post_video_empty_url`**
   - **목적**: 빈 URL로 POST 요청 시 422 에러 확인
   - **테스트 방법**: 빈 문자열을 포함한 JSON 요청
   - **검증**: 상태 코드 422, 에러 메시지 포함

3. **`test_post_video_invalid_url_format_text`**
   - **목적**: 텍스트만 있는 URL로 POST 요청 시 422 에러 확인
   - **테스트 방법**: URL 형식이 아닌 텍스트를 포함한 JSON 요청
   - **검증**: 상태 코드 422, 에러 메시지 포함

4. **`test_post_video_invalid_url_format_no_scheme`**
   - **목적**: scheme 없는 URL로 POST 요청 시 422 에러 확인
   - **테스트 방법**: http:// 또는 https:// 없는 URL 요청
   - **검증**: 상태 코드 422, 에러 메시지 포함

5. **`test_post_video_no_video_id`**
   - **목적**: Video ID가 없는 URL로 POST 요청 시 422 에러 확인
   - **테스트 방법**: v= 파라미터가 없는 YouTube URL 요청
   - **검증**: 상태 코드 422, 에러 메시지 포함

6. **`test_post_video_non_youtube_url`**
   - **목적**: YouTube가 아닌 URL로 POST 요청 시 422 에러 확인
   - **테스트 방법**: 다른 도메인의 URL 요청
   - **검증**: 상태 코드 422, 에러 메시지 포함

#### POST /api/video/{video_id}/transcript 엔드포인트 테스트

7. **`test_post_get_video_transcript_success`**
   - **목적**: 정상적인 Video ID로 자막 추출 요청 시 성공 응답 확인
   - **테스트 방법**: 실행 중인 서버에 HTTP POST 요청
   - **검증**:
     - 상태 코드 200
     - 응답에 `video_id`, `transcript`, `status`, `language` 포함
     - `status`가 "success"
     - `transcript`에 자막 텍스트 존재
     - `language`가 "en"

8. **`test_post_get_video_transcript_invalid_video_id`**
   - **목적**: 존재하지 않는 Video ID로 자막 추출 요청 시 400 에러 확인
   - **테스트 방법**: 존재하지 않는 Video ID로 요청
   - **검증**: 
     - 상태 코드 400
     - 에러 메시지 포함 (사용자 친화적 메시지)

#### POST /api/video/{video_id}/vocabulary 엔드포인트 테스트

9. **`test_post_generate_vocabulary_success`**
   - **목적**: 정상적인 Video ID로 단어장 생성 요청 시 성공 응답 확인
   - **테스트 방법**: 실행 중인 서버에 HTTP POST 요청
   - **주의사항**: 
     - LLM 처리가 필요하므로 시간이 오래 걸릴 수 있습니다 (수십 초 ~ 수분)
     - vLLM 서버가 실행 중이어야 합니다
     - 서버가 실행 중이지 않으면 자동으로 스킵됩니다
   - **검증**:
     - 상태 코드 200
     - 응답에 `video_id`, `words`, `phrases`, `status` 포함
     - `status`가 "success"
     - `words`와 `phrases`가 리스트 형식
     - 각 단어 엔트리에 `word`, `pos`, `meanings`, `synonyms`, `example` 포함
     - 각 숙어 엔트리에 `phrase`, `meaning`, `example` 포함

10. **`test_post_generate_vocabulary_invalid_video_id`**
    - **목적**: 존재하지 않는 Video ID로 단어장 생성 요청 시 400 에러 확인
    - **테스트 방법**: 존재하지 않는 Video ID로 요청
    - **검증**: 
      - 상태 코드 400
      - 에러 메시지 포함 (사용자 친화적 메시지)

**테스트 실행 전 준비사항**:
```bash
# 터미널 1: FastAPI 서버 실행
uvicorn app.main:app --reload

# 터미널 2: vLLM 서버 실행 확인 (vocabulary 엔드포인트 테스트의 경우)
# vLLM 서버가 실행 중이어야 합니다 (app/core/config.py의 VLLM_SERVER_URL 확인)

# 터미널 3: 테스트 실행
# 전체 테스트 실행
pytest tests/test_routes/test_video.py -v -s

# vocabulary 엔드포인트 테스트만 실행
pytest tests/test_routes/test_video.py::test_post_generate_vocabulary_success -v -s
pytest tests/test_routes/test_video.py::test_post_generate_vocabulary_invalid_video_id -v -s
```

**서버 실행 여부 확인**:
- 테스트는 자동으로 서버 실행 여부를 확인합니다 (`/health` 엔드포인트 사용)
- 서버가 실행 중이지 않으면 해당 테스트는 자동으로 스킵됩니다
- vocabulary 엔드포인트 테스트는 vLLM 서버도 실행 중이어야 합니다

---

### `test_services/test_llm_prompts.py` - LLM 프롬프트 규칙 테스트

**파일 경로**: `tests/test_services/test_llm_prompts.py`

**목적**: 프롬프트 수정 시 규칙 누락을 빠르게 감지하기 위한 초경량 단위 테스트입니다.

**테스트 대상**:
- `app/services/llm/prompts.py`의 `get_word_extraction_prompt`
- `app/services/llm/prompts.py`의 `get_phrase_extraction_prompt`

**주요 테스트 모듈**:

1. **`test_word_prompt_enforces_unique_meanings`**
   - **목적**: 단어 추출 프롬프트에 "중복 의미 제거" 규칙이 포함되어 있는지 확인
   - **검증**: `"중복"`, `"최대 2개"`, `"하나만 유지"` 구문 존재 여부

2. **`test_phrase_prompt_enforces_multi_token_rule`**
   - **목적**: 숙어 추출 프롬프트가 다단어 표현만 허용하도록 안내하는지 확인
   - **검증**: `"두 단어 이상"`, `"단일 단어"`, `"최소 두 개"` 구문 존재 여부

**테스트 방법**:
- 실질적인 LLM 호출 없이 문자열만 확인하므로 매우 빠르게 실행됩니다.
- 프롬프트를 수정할 때마다 `pytest tests/test_services/test_llm_prompts.py -v`로 회귀 테스트를 수행하세요.

---

### `test_services/test_llm_extract_words.py` - 단어 추출 모듈 테스트

**파일 경로**: `tests/test_services/test_llm_extract_words.py`

**목적**: 1단계 단어 추출 기능을 실제 vLLM 서버와 연동하여 테스트합니다.

**중요**: 이 테스트는 **vLLM 서버가 실행 중**이어야 합니다. 서버가 없으면 자동으로 스킵됩니다.

**테스트 대상**:
- `app/services/llm/extract_words.py`의 `extract_words_from_chunks` 함수
- 여러 청크를 병렬로 처리하여 단어 추출
- 결과 구조 검증 (품사, 뜻 포함)

**주요 테스트 모듈**:

1. **`test_extract_words_from_chunks_success`**
   - **목적**: 정상적인 청크 텍스트로 단어 추출 시 성공 응답 확인
   - **검증**: 
     - 응답에 `videoId`, `result` 필드 포함
     - 단어가 추출되었는지 확인
     - 각 단어의 구조가 올바른지 확인 (품사, 뜻)

2. **`test_extract_words_from_chunks_empty_chunks`**
   - **목적**: 빈 청크 리스트 처리 확인
   - **검증**: 빈 결과가 올바르게 반환됨

3. **`test_extract_words_from_chunks_single_chunk`**
   - **목적**: 단일 청크 처리 확인
   - **검증**: 단일 청크도 정상적으로 처리됨

4. **`test_extract_words_result_structure`**
   - **목적**: 결과 구조 검증
   - **검증**: 
     - 품사는 "n", "v", "adj", "adv" 중 하나
     - 뜻은 리스트이며 최대 2개

**테스트 실행 전 준비사항**:
```bash
# vLLM 서버가 실행 중이어야 함
# 설정: app/core/config.py의 VLLM_SERVER_URL 확인

# 테스트 실행
pytest tests/test_services/test_llm_extract_words.py -v -s
```

---

### `test_services/test_llm_extract_phrases.py` - 숙어 추출 모듈 테스트

**파일 경로**: `tests/test_services/test_llm_extract_phrases.py`

**목적**: 1단계 숙어 추출 기능을 실제 vLLM 서버와 연동하여 테스트합니다.

**중요**: 이 테스트는 **vLLM 서버가 실행 중**이어야 합니다. 서버가 없으면 자동으로 스킵됩니다.

**테스트 대상**:
- `app/services/llm/extract_phrases.py`의 `extract_phrases_from_chunks` 함수
- 여러 청크를 병렬로 처리하여 숙어 추출
- 결과 구조 검증 (두 단어 이상, 뜻 포함)

**주요 테스트 모듈**:

1. **`test_extract_phrases_from_chunks_success`**
   - **목적**: 정상적인 청크 텍스트로 숙어 추출 시 성공 응답 확인
   - **검증**: 
     - 응답에 `videoId`, `result` 필드 포함
     - 숙어가 추출되었는지 확인
     - 각 숙어가 두 단어 이상인지 확인

2. **`test_extract_phrases_from_chunks_empty_chunks`**
   - **목적**: 빈 청크 리스트 처리 확인
   - **검증**: 빈 결과가 올바르게 반환됨

3. **`test_extract_phrases_result_structure`**
   - **목적**: 결과 구조 검증
   - **검증**: 
     - 모든 숙어가 두 단어 이상
     - 뜻은 문자열 또는 리스트

**테스트 실행 전 준비사항**:
```bash
# vLLM 서버가 실행 중이어야 함
# 설정: app/core/config.py의 VLLM_SERVER_URL 확인

# 테스트 실행
pytest tests/test_services/test_llm_extract_phrases.py -v -s
```

---

### `test_services/test_llm_enrich_words.py` - 단어 상세 정보 생성 모듈 테스트

**파일 경로**: `tests/test_services/test_llm_enrich_words.py`

**목적**: 2단계 단어 상세 정보 생성 기능을 실제 vLLM 서버와 연동하여 테스트합니다.

**중요**: 이 테스트는 **vLLM 서버가 실행 중**이어야 합니다. 서버가 없으면 자동으로 스킵됩니다.

**테스트 대상**:
- `app/services/llm/enrich_words.py`의 `enrich_words` 함수
- 1단계 단어 추출 결과에 동의어와 예문 추가
- 결과 구조 검증 (동의어 최대 2개, 예문 포함)

**주요 테스트 모듈**:

1. **`test_enrich_words_success`**
   - **목적**: 정상적인 1단계 결과로 단어 상세 정보 생성 시 성공 응답 확인
   - **검증**: 
     - 응답에 `videoId`, `result` 필드 포함
     - 각 단어에 동의어와 예문이 포함됨
     - 동의어는 최대 2개
     - 예문은 영어 문자열

2. **`test_enrich_words_empty_result`**
   - **목적**: 빈 1단계 결과 처리 확인
   - **검증**: 빈 결과가 올바르게 반환됨

3. **`test_enrich_words_result_structure`**
   - **목적**: 결과 구조 검증
   - **검증**: 
     - 모든 단어에 동의어와 예문 포함
     - 동의어는 최대 2개
     - 예문은 영어 문자열

**테스트 실행 전 준비사항**:
```bash
# vLLM 서버가 실행 중이어야 함
# 설정: app/core/config.py의 VLLM_SERVER_URL 확인

# 테스트 실행
pytest tests/test_services/test_llm_enrich_words.py -v -s
```

---

### `test_services/test_llm_enrich_phrases.py` - 숙어 예문 생성 모듈 테스트

**파일 경로**: `tests/test_services/test_llm_enrich_phrases.py`

**목적**: 2단계 숙어 예문 생성 기능을 실제 vLLM 서버와 연동하여 테스트합니다.

**중요**: 이 테스트는 **vLLM 서버가 실행 중**이어야 합니다. 서버가 없으면 자동으로 스킵됩니다.

**테스트 대상**:
- `app/services/llm/enrich_phrases.py`의 `enrich_phrases` 함수
- 1단계 숙어 추출 결과에 예문 추가
- 결과 구조 검증 (예문 포함)

**주요 테스트 모듈**:

1. **`test_enrich_phrases_success`**
   - **목적**: 정상적인 1단계 결과로 숙어 예문 생성 시 성공 응답 확인
   - **검증**: 
     - 응답에 `videoId`, `result` 필드 포함
     - 각 숙어에 예문이 포함됨
     - 예문은 영어 문자열

2. **`test_enrich_phrases_empty_result`**
   - **목적**: 빈 1단계 결과 처리 확인
   - **검증**: 빈 결과가 올바르게 반환됨

3. **`test_enrich_phrases_result_structure`**
   - **목적**: 결과 구조 검증
   - **검증**: 
     - 모든 숙어에 예문 포함
     - 예문은 영어 문자열

**테스트 실행 전 준비사항**:
```bash
# vLLM 서버가 실행 중이어야 함
# 설정: app/core/config.py의 VLLM_SERVER_URL 확인

# 테스트 실행
pytest tests/test_services/test_llm_enrich_phrases.py -v -s
```

---

### `test_services/test_llm_prompt_ab_test.py` - 프롬프트 A/B 테스트

**파일 경로**: `tests/test_services/test_llm_prompt_ab_test.py`

**목적**: 프롬프트의 여러 버전을 A/B 테스트하여 최적의 프롬프트 버전을 찾습니다.

**중요**: 이 테스트는 **vLLM 서버가 실행 중**이어야 합니다. 서버가 없으면 자동으로 스킵됩니다.

**관련 파일**:
- `tests/test_services/test_llm_prompt_ab_test_prompts.py`: A/B 테스트용 프롬프트 함수들 (40개 버전)
- `tests/test_services/ab_test_results/`: 테스트 결과 저장 디렉토리

**테스트 대상**:
- 1단계 프롬프트: 단어 추출, 숙어 추출 (각 10개 버전)
- 2단계 프롬프트: 단어 상세 정보 생성, 숙어 예문 생성 (각 10개 버전)
- 각 프롬프트 버전을 10번씩 실행하여 성공률 측정

**주요 테스트 모듈**:

1. **`test_stage1_prompt_ab_test`**
   - **목적**: 1단계 프롬프트 (단어 추출, 숙어 추출) A/B 테스트
   - **사용 Fixture**: `skip_if_vllm_unavailable`, `ab_test_chunk_text`, `ab_test_video_id`
   - **검증**: 
     - 각 프롬프트 버전의 성공률 측정
     - JSON 파싱 성공/실패 기록
     - 테스트 결과 JSON 파일 생성

2. **`test_stage2_prompt_ab_test`**
   - **목적**: 2단계 프롬프트 (단어 상세 정보 생성, 숙어 예문 생성) A/B 테스트
   - **사용 Fixture**: `skip_if_vllm_unavailable`, `mock_word_extraction_result`, `mock_phrase_extraction_result`, `ab_test_video_id`
   - **검증**: 
     - 각 프롬프트 버전의 성공률 측정
     - JSON 파싱 성공/실패 기록
     - 테스트 결과 JSON 파일 생성

**테스트 실행 전 준비사항**:
```bash
# vLLM 서버가 실행 중이어야 함
# 설정: app/core/config.py의 VLLM_SERVER_URL 확인

# 전체 A/B 테스트 실행
pytest tests/test_services/test_llm_prompt_ab_test.py -v -s

# 1단계만 테스트
pytest tests/test_services/test_llm_prompt_ab_test.py::test_stage1_prompt_ab_test -v -s

# 2단계만 테스트
pytest tests/test_services/test_llm_prompt_ab_test.py::test_stage2_prompt_ab_test -v -s
```

**출력 결과**:
- 테스트 결과는 `tests/test_services/ab_test_results/ab_test_results_stage1_YYYYMMDD_HHMMSS.json` 또는 `ab_test_results_stage2_YYYYMMDD_HHMMSS.json` 파일로 저장됩니다.
- 각 프롬프트 버전별 성공률, 실패 원인, 전체 실패 응답 내용이 포함됩니다.
- 실패한 케이스의 전체 LLM 응답 내용이 기록되어 분석이 용이합니다.

---

### `test_services/test_llm_prompt_ab_test_prompts.py` - A/B 테스트용 프롬프트 함수들

**파일 경로**: `tests/test_services/test_llm_prompt_ab_test_prompts.py`

**목적**: A/B 테스트에서 사용하는 프롬프트 함수들을 정의합니다.

**내용**:
- 단어 추출 프롬프트 10개 버전 (`get_word_extraction_prompt_v1` ~ `v10`)
- 숙어 추출 프롬프트 10개 버전 (`get_phrase_extraction_prompt_v1` ~ `v10`)
- 단어 상세 정보 생성 프롬프트 10개 버전 (`get_word_enrichment_prompt_v1` ~ `v10`)
- 숙어 예문 생성 프롬프트 10개 버전 (`get_phrase_enrichment_prompt_v1` ~ `v10`)

**설명**:
- 이 파일은 `practice/phase4/prompt_ab_test.py`에서 추출한 프롬프트 함수들을 포함합니다.
- `test_llm_prompt_ab_test.py`에서 직접 import하여 사용합니다.
- 각 프롬프트 버전은 JSON 형식 강조 위치, 예시 포함 여부, 실패 예시 포함 여부 등에 따라 차별화됩니다.

---

### `test_services/conftest.py` - LLM 서비스 테스트 전용 Fixture

**파일 경로**: `tests/test_services/conftest.py`

**목적**: LLM 서비스 테스트에서 사용하는 공통 fixture를 정의합니다.

**정의된 Fixture**:

#### 일반 테스트용 Fixture

1. **`sample_chunk_texts`**
   - **타입**: `List[str]`
   - **용도**: 테스트용 샘플 청크 텍스트 리스트 (8개 청크)
   - **값**: 다양한 단어와 숙어가 포함된 샘플 데이터

2. **`sample_video_id`**
   - **타입**: `str`
   - **용도**: 테스트용 샘플 Video ID
   - **값**: `"test_video_123"`

3. **`vllm_server_available`** (session scope)
   - **타입**: `bool`
   - **용도**: vLLM 서버가 실행 중인지 확인
   - **반환**: 서버가 사용 가능하면 `True`, 아니면 `False`
   - **설명**: `app/core/config.py`의 `VLLM_SERVER_URL` 설정을 참고하여 서버 연결 확인
   - **확인 방법**: `/health`, `/v1/models`, `/v1/chat/completions` 엔드포인트를 순차적으로 확인

4. **`skip_if_vllm_unavailable`**
   - **타입**: `bool`
   - **용도**: vLLM 서버가 사용 불가능하면 테스트를 자동으로 스킵
   - **설명**: 이 fixture를 사용하는 테스트는 서버가 없으면 자동으로 스킵됩니다.

#### A/B 테스트용 Fixture

5. **`ab_test_chunk_text`**
   - **타입**: `str`
   - **용도**: A/B 테스트용 긴 청크 텍스트 (약 1,200자)
   - **값**: 단어와 숙어가 적절한 비율로 포함된 긴 텍스트
   - **설명**: 프롬프트 A/B 테스트에서 사용하는 표준 테스트 데이터

6. **`ab_test_video_id`**
   - **타입**: `str`
   - **용도**: A/B 테스트용 Video ID
   - **값**: `"ab_test_video_001"`

7. **`mock_word_extraction_result`**
   - **타입**: `Dict[str, Any]`
   - **용도**: A/B 테스트용 단어 추출 결과 목업 (50개 단어)
   - **값**: 1단계 단어 추출 결과 형식의 목업 데이터
   - **설명**: 2단계 단어 상세 정보 생성 프롬프트 테스트에 사용

8. **`mock_phrase_extraction_result`**
   - **타입**: `Dict[str, Any]`
   - **용도**: A/B 테스트용 숙어 추출 결과 목업 (18개 숙어)
   - **값**: 1단계 숙어 추출 결과 형식의 목업 데이터
   - **설명**: 2단계 숙어 예문 생성 프롬프트 테스트에 사용

**사용 예시**:
```python
@pytest.mark.asyncio
async def test_llm_function(skip_if_vllm_unavailable, sample_chunk_texts, sample_video_id):
    """vLLM 서버가 없으면 자동으로 스킵됨"""
    # 테스트 코드
    result = await extract_words_from_chunks(sample_chunk_texts, sample_video_id)
    assert result is not None

@pytest.mark.asyncio
async def test_ab_test(skip_if_vllm_unavailable, ab_test_chunk_text, ab_test_video_id):
    """A/B 테스트용 fixture 사용"""
    # A/B 테스트 코드
    pass
```

---

**[↑ 목차로 돌아가기](#📋-목차)**

---

## ⚙️ conftest.py 설정 파일 설명

`conftest.py`는 pytest의 핵심 설정 파일입니다. 이 파일에 정의된 fixture는 해당 폴더와 하위 폴더의 모든 테스트에서 자동으로 사용할 수 있습니다.

### pytest의 conftest.py 동작 원리

1. **자동 인식**: pytest는 테스트 실행 시 `conftest.py` 파일을 자동으로 찾아서 로드합니다.
2. **스코프**: 각 폴더의 `conftest.py`는 해당 폴더와 하위 폴더에서만 유효합니다.
3. **상속**: 하위 폴더는 상위 폴더의 `conftest.py`도 자동으로 상속받습니다.

### `tests/conftest.py` - 전체 공통 Fixture

**파일 경로**: `tests/conftest.py`

**목적**: 모든 테스트에서 공통으로 사용할 fixture를 정의합니다.

**사용 위치**:
- `tests/test_main.py`
- `tests/test_models/` (일부 fixture 사용)
- `tests/test_routes/` (일부 fixture 사용)
- `tests/test_services/` (향후)

**정의된 Fixture**:

#### 1. `client` Fixture

```python
@pytest.fixture
def client():
    """FastAPI 테스트 클라이언트 (서버 없이 인메모리 테스트)"""
    return TestClient(app)
```

**설명**:
- **타입**: `TestClient` (FastAPI 제공)
- **용도**: 서버를 실행하지 않고 FastAPI 앱을 인메모리에서 테스트
- **장점**: 빠른 실행 속도, 외부 의존성 없음
- **단점**: 실제 네트워크 레벨의 테스트 불가

**사용 예시**:
```python
def test_endpoint(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
```

**테스트 대상**:
- `app/main.py`의 FastAPI 앱 전체
- 모든 API 엔드포인트의 요청/응답 테스트

---

#### 2. `running_server_client` Fixture

```python
@pytest.fixture
def running_server_client():
    """이미 실행 중인 서버에 HTTP 요청을 보내는 클라이언트"""
    base_url = "http://localhost:8000"
    with httpx.Client(base_url=base_url, timeout=10.0) as client:
        yield client
```

**설명**:
- **타입**: `httpx.Client` (HTTP 클라이언트)
- **용도**: 실제로 실행 중인 서버에 HTTP 요청을 보냄
- **장점**: 실제 네트워크 레벨의 통합 테스트 가능
- **단점**: 서버가 실행 중이어야 함

**사용법**:
1. 터미널에서 서버 실행: `uvicorn app.main:app --reload`
2. 다른 터미널에서 pytest 실행: `pytest tests/test_routes/test_video.py -v -s`
3. 테스트 코드에서 이 fixture 사용하면 실행 중인 서버로 요청 보냄

**주의사항**:
- 서버가 실행 중이어야 함
- 기본 포트: 8000 (다른 포트면 `conftest.py`에서 수정 필요)
- 타임아웃: 10초

**사용 예시**:
```python
def test_endpoint(running_server_client: httpx.Client):
    response = running_server_client.get("/health")
    assert response.status_code == 200
```

**테스트 대상**:
- 실제로 실행 중인 uvicorn 서버 (`app/main.py`)
- 네트워크 레벨의 통합 테스트

---

### `tests/test_models/conftest.py` - 모델 테스트 전용 Fixture

**파일 경로**: `tests/test_models/conftest.py`

**목적**: 모델/스키마 테스트에서만 사용하는 fixture를 정의합니다.

**사용 위치**:
- `tests/test_models/test_schemas.py`

**정의된 Fixture**:

#### 1. `sample_youtube_url` Fixture

```python
@pytest.fixture
def sample_youtube_url():
    """정상적인 YouTube URL (전체 URL 형식)"""
    return "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

**설명**:
- **타입**: `str`
- **용도**: 정상 케이스 테스트용 YouTube URL
- **값**: `"https://www.youtube.com/watch?v=dQw4w9WgXcQ"` (Rick Astley - Never Gonna Give You Up)

**사용 예시**:
```python
def test_success(sample_youtube_url):
    data = VideoUrlRequests(url=sample_youtube_url)
    assert data.url == sample_youtube_url
```

---

#### 2. `sample_youtube_short_url` Fixture

```python
@pytest.fixture
def sample_youtube_short_url():
    """youtu.be 형식의 YouTube URL (에러 케이스용)"""
    return "https://youtu.be/dQw4w9WgXcQ"
```

**설명**:
- **타입**: `str`
- **용도**: 에러 케이스 테스트용 (youtu.be 형식은 허용하지 않음)
- **값**: `"https://youtu.be/dQw4w9WgXcQ"`

**사용 예시**:
```python
def test_youtube_short_url(sample_youtube_short_url):
    with pytest.raises(ValidationError):
        VideoUrlRequests(url=sample_youtube_short_url)
```

---

#### 3. `sample_video_id` Fixture

```python
@pytest.fixture
def sample_video_id():
    """Video ID만 추출된 값"""
    return "dQw4w9WgXcQ"
```

**설명**:
- **타입**: `str`
- **용도**: Video ID 관련 테스트용
- **값**: `"dQw4w9WgXcQ"`

---

#### 4. `invalid_url` Fixture

```python
@pytest.fixture
def invalid_url():
    """YouTube가 아닌 URL (에러 케이스용)"""
    return "https://invalid-url.com"
```

**설명**:
- **타입**: `str`
- **용도**: 에러 케이스 테스트용 (YouTube가 아닌 도메인)
- **값**: `"https://invalid-url.com"`

---

#### 5. `empty_string` Fixture

```python
@pytest.fixture
def empty_string():
    """빈 문자열 (에러 케이스용)"""
    return ""
```

**설명**:
- **타입**: `str`
- **용도**: 빈 값 검증 테스트용
- **값**: `""`

---

#### 6. `whitespace_only` Fixture

```python
@pytest.fixture
def whitespace_only():
    """공백만 있는 문자열 (에러 케이스용)"""
    return "   "
```

**설명**:
- **타입**: `str`
- **용도**: 공백만 있는 문자열 검증 테스트용
- **값**: `"   "` (공백 3개)

---

#### 7. `invalid_url_format_text` Fixture

```python
@pytest.fixture
def invalid_url_format_text():
    """텍스트만 있는 값 (에러 케이스용)"""
    return "그냥 텍스트"
```

**설명**:
- **타입**: `str`
- **용도**: URL 형식이 아닌 텍스트 검증 테스트용
- **값**: `"그냥 텍스트"`

---

#### 8. `invalid_url_format_no_scheme` Fixture

```python
@pytest.fixture
def invalid_url_format_no_scheme():
    """scheme(http://) 없는 URL (에러 케이스용)"""
    return "youtube.com"
```

**설명**:
- **타입**: `str`
- **용도**: scheme 없는 URL 검증 테스트용
- **값**: `"youtube.com"`

---

#### 9. `youtube_url_without_www` Fixture

```python
@pytest.fixture
def youtube_url_without_www():
    """www 없이 youtube.com만 있는 URL (에러 케이스용)"""
    return "https://youtube.com/watch?v=dQw4w9WgXcQ"
```

**설명**:
- **타입**: `str`
- **용도**: www 없는 YouTube URL 검증 테스트용 (www.youtube.com만 허용)
- **값**: `"https://youtube.com/watch?v=dQw4w9WgXcQ"`

---

#### 10. `youtube_url_wrong_path` Fixture

```python
@pytest.fixture
def youtube_url_wrong_path():
    """잘못된 경로(/embed)를 가진 YouTube URL (에러 케이스용)"""
    return "https://www.youtube.com/embed/dQw4w9WgXcQ"
```

**설명**:
- **타입**: `str`
- **용도**: 잘못된 경로를 가진 YouTube URL 검증 테스트용 (/watch만 허용)
- **값**: `"https://www.youtube.com/embed/dQw4w9WgXcQ"`

---

#### 11. `youtube_url_no_v_param` Fixture

```python
@pytest.fixture
def youtube_url_no_v_param():
    """v 파라미터가 없는 YouTube URL (에러 케이스용)"""
    return "https://www.youtube.com/watch"
```

**설명**:
- **타입**: `str`
- **용도**: v 파라미터가 없는 YouTube URL 검증 테스트용
- **값**: `"https://www.youtube.com/watch"`

---

### `tests/test_routes/conftest.py` - 라우트 테스트 전용 Fixture

**파일 경로**: `tests/test_routes/conftest.py`

**목적**: 라우트 테스트에서만 사용하는 fixture를 정의합니다.

**사용 위치**:
- `tests/test_routes/test_video.py`

**정의된 Fixture**:

#### 1. `sample_youtube_url` Fixture

```python
@pytest.fixture
def sample_youtube_url():
    """정상적인 YouTube URL (전체 URL 형식)"""
    return "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

**설명**:
- **타입**: `str`
- **용도**: 정상 케이스 테스트용 YouTube URL
- **값**: `"https://www.youtube.com/watch?v=dQw4w9WgXcQ"`

**사용 예시**:
```python
def test_post_video_success(running_server_client, sample_youtube_url):
    response = running_server_client.post(
        "/api/video",
        json={"url": sample_youtube_url}
    )
    assert response.status_code == 200
```

---

#### 2. `empty_string` Fixture

```python
@pytest.fixture
def empty_string():
    """빈 문자열 (에러 케이스용)"""
    return ""
```

**설명**:
- **타입**: `str`
- **용도**: 빈 URL 검증 테스트용
- **값**: `""`

---

#### 3. `invalid_url_format_text` Fixture

```python
@pytest.fixture
def invalid_url_format_text():
    """텍스트만 있는 값 (에러 케이스용)"""
    return "그냥 텍스트"
```

**설명**:
- **타입**: `str`
- **용도**: URL 형식이 아닌 텍스트 검증 테스트용
- **값**: `"그냥 텍스트"`

---

#### 4. `invalid_url_format_no_scheme` Fixture

```python
@pytest.fixture
def invalid_url_format_no_scheme():
    """scheme(http://) 없는 URL (에러 케이스용)"""
    return "youtube.com"
```

**설명**:
- **타입**: `str`
- **용도**: scheme 없는 URL 검증 테스트용
- **값**: `"youtube.com"`

---

#### 5. `sample_video_id` Fixture

```python
@pytest.fixture
def sample_video_id():
    """정상적인 YouTube Video ID (자막이 있는 영상)"""
    return "dQw4w9WgXcQ"  # Rick Astley - Never Gonna Give You Up (자막 있음)
```

**설명**:
- **타입**: `str`
- **용도**: 정상 케이스 테스트용 Video ID (자막이 있는 영상)
- **값**: `"dQw4w9WgXcQ"`

**사용 예시**:
```python
def test_post_get_video_transcript_success(running_server_client, sample_video_id):
    response = running_server_client.post(
        f"/api/video/{sample_video_id}/transcript"
    )
    assert response.status_code == 200
```

---

#### 6. `invalid_video_id` Fixture

```python
@pytest.fixture
def invalid_video_id():
    """존재하지 않는 YouTube Video ID (에러 케이스용)"""
    return "INVALID_VIDEO_ID_12345"
```

**설명**:
- **타입**: `str`
- **용도**: 에러 케이스 테스트용 (존재하지 않는 Video ID)
- **값**: `"INVALID_VIDEO_ID_12345"`

**사용 예시**:
```python
def test_post_get_video_transcript_invalid_video_id(running_server_client, invalid_video_id):
    response = running_server_client.post(
        f"/api/video/{invalid_video_id}/transcript"
    )
    assert response.status_code == 400
```

---

#### 7. `server_available` Fixture (session scope)

```python
@pytest.fixture(scope="session")
def server_available():
    """FastAPI 서버가 실행 중인지 확인하는 fixture"""
    # /health 엔드포인트로 서버 실행 여부 확인
    return True or False
```

**설명**:
- **타입**: `bool`
- **용도**: FastAPI 서버가 실행 중인지 확인
- **반환**: 서버가 사용 가능하면 `True`, 아니면 `False`
- **확인 방법**: `/health` 엔드포인트로 서버 연결 확인
- **스코프**: `session` (테스트 세션당 한 번만 확인)

**사용 예시**:
```python
@pytest.mark.skipif(not server_available(), reason="서버가 실행 중이지 않습니다")
def test_endpoint(server_available, running_server_client):
    # 서버가 없으면 자동으로 스킵됨
    response = running_server_client.get("/health")
    assert response.status_code == 200
```

---

#### 8. `skip_if_server_unavailable` Fixture

```python
@pytest.fixture
def skip_if_server_unavailable(server_available):
    """서버가 사용 불가능하면 테스트를 자동으로 스킵하는 fixture"""
    if not server_available:
        pytest.skip("서버가 실행 중이지 않습니다...")
    return True
```

**설명**:
- **타입**: `bool` (항상 `True` 반환, 서버가 없으면 스킵)
- **용도**: 서버가 실행 중이지 않으면 테스트를 자동으로 스킵
- **의존성**: `server_available` fixture 사용
- **동작**: 서버가 없으면 `pytest.skip()` 호출하여 테스트 스킵

**사용 예시**:
```python
def test_endpoint(skip_if_server_unavailable, running_server_client):
    """서버가 없으면 자동으로 스킵됨"""
    response = running_server_client.get("/health")
    assert response.status_code == 200
```

---

**[↑ 목차로 돌아가기](#📋-목차)**

---

## 🚀 테스트 실행 방법

테스트를 실행하는 다양한 방법을 상황별로 설명합니다.

### 기본 실행 방법

#### 1. 모든 테스트 실행

```bash
pytest
```

**설명**:
- `tests/` 폴더 내의 모든 테스트 파일을 실행합니다.
- 가장 간단한 방법이지만 모든 테스트가 실행되므로 시간이 걸릴 수 있습니다.

**실행 결과 예시**:
```
========================= test session starts ==========================
platform darwin -- Python 3.12.11, pytest-7.4.0, pluggy-1.3.0
rootdir: /Users/datahyeon/Project/youtube-vocabulary-generator
collected 15 items

tests/test_main.py::test_app_startup PASSED                      [  6%]
tests/test_main.py::test_health_check PASSED                     [ 13%]
tests/test_models/test_schemas.py::test_video_url_request_success PASSED [ 20%]
...
========================= 15 passed in 2.34s ==========================
```

---

#### 2. 특정 테스트 파일 실행

```bash
pytest tests/test_routes/test_video.py
```

**설명**:
- 특정 테스트 파일만 실행합니다.
- 파일 경로를 지정하면 해당 파일의 모든 테스트 함수가 실행됩니다.

**실행 결과 예시**:
```
========================= test session starts ==========================
collected 8 items

tests/test_routes/test_video.py::test_post_video_success PASSED        [ 12%]
tests/test_routes/test_video.py::test_post_video_empty_url PASSED       [ 25%]
...
========================= 8 passed in 1.23s ==========================
```

---

#### 3. 특정 테스트 함수 실행

```bash
pytest tests/test_routes/test_video.py::test_post_video_success
```

**설명**:
- 특정 테스트 함수만 실행합니다.
- `::` 구분자를 사용하여 파일 경로와 함수명을 구분합니다.

**실행 결과 예시**:
```
========================= test session starts ==========================
collected 1 item

tests/test_routes/test_video.py::test_post_video_success PASSED         [100%]

========================= 1 passed in 0.45s ==========================
```

---

#### 4. 특정 폴더의 모든 테스트 실행

```bash
pytest tests/test_models/
```

**설명**:
- 특정 폴더 내의 모든 테스트 파일을 실행합니다.
- 폴더 경로를 지정하면 해당 폴더와 하위 폴더의 모든 테스트가 실행됩니다.

**실행 결과 예시**:
```
========================= test session starts ==========================
collected 12 items

tests/test_models/test_schemas.py::test_video_url_request_success PASSED [  8%]
tests/test_models/test_schemas.py::test_video_url_request_empty_string PASSED [ 16%]
...
========================= 12 passed in 0.89s ==========================
```

---

#### 5. 키워드로 테스트 필터링

```bash
pytest -k "video"
```

**설명**:
- 테스트 함수명에 특정 키워드가 포함된 테스트만 실행합니다.
- `-k` 옵션을 사용하여 필터링합니다.

**실행 결과 예시**:
```
========================= test session starts ==========================
collected 15 items / 8 deselected / 7 selected

tests/test_routes/test_video.py::test_post_video_success PASSED         [ 14%]
tests/test_routes/test_video.py::test_post_get_video_transcript_success PASSED [ 28%]
...
========================= 7 passed in 1.12s ==========================
```

---

### 실행 중인 서버를 대상으로 하는 테스트

**중요**: `test_routes/test_video.py`의 테스트는 **실행 중인 서버**를 대상으로 합니다.

#### 실행 방법

**1단계: 서버 실행 (터미널 1)**
```bash
uvicorn app.main:app --reload
```

서버가 `http://localhost:8000`에서 실행되어야 합니다.

**2단계: 테스트 실행 (터미널 2)**
```bash
# 전체 비디오 라우트 테스트 실행
pytest tests/test_routes/test_video.py -v -s

# 특정 테스트만 실행
pytest tests/test_routes/test_video.py::test_post_video_success -v -s
pytest tests/test_routes/test_video.py::test_post_get_video_transcript_success -v -s
```

**옵션 설명**:
- `-v`: 상세 출력 (verbose) - 각 테스트의 이름과 결과를 자세히 표시
- `-s`: print 출력 표시 (capture=no) - 테스트 코드의 `print()` 문이 출력됨

**실행 결과 예시**:
```
========================= test session starts ==========================
collected 8 items

tests/test_routes/test_video.py::test_post_video_success PASSED        [ 12%]

[테스트 결과] POST /api/video (정상 케이스)
요청 URL: https://www.youtube.com/watch?v=dQw4w9WgXcQ
상태 코드: 200
응답 내용: {'video_id': 'dQw4w9WgXcQ', 'status': 'success', 'message': None}
✅ 정상 케이스 테스트 성공!

...
========================= 8 passed in 3.45s ==========================
```

---

**[↑ 목차로 돌아가기](#📋-목차)**

---

## 📊 테스트 실행 옵션 및 결과 해석

pytest는 다양한 옵션을 제공하여 테스트 실행 방식을 제어할 수 있습니다. 각 옵션의 목적과 결과를 상세히 설명합니다.

### 출력 모드 옵션

#### 1. 기본 출력 모드 (기본값)

```bash
pytest tests/test_routes/test_video.py
```

**출력 예시**:
```
========================= test session starts ==========================
collected 8 items

tests/test_routes/test_video.py::test_post_video_success PASSED        [ 12%]
tests/test_routes/test_video.py::test_post_video_empty_url PASSED      [ 25%]
...
========================= 8 passed in 3.45s ==========================
```

**설명**:
- 각 테스트의 이름과 결과만 표시됩니다.
- `print()` 문의 출력은 표시되지 않습니다.
- 가장 간결한 출력 형식입니다.

---

#### 2. 상세 출력 모드 (`-v` 또는 `--verbose`)

```bash
pytest tests/test_routes/test_video.py -v
```

**출력 예시**:
```
========================= test session starts ==========================
platform darwin -- Python 3.12.11, pytest-7.4.0, pluggy-1.3.0
rootdir: /Users/datahyeon/Project/youtube-vocabulary-generator
collected 8 items

tests/test_routes/test_video.py::test_post_video_success PASSED        [ 12%]
tests/test_routes/test_video.py::test_post_video_empty_url PASSED      [ 25%]
tests/test_routes/test_video.py::test_post_video_invalid_url_format_text PASSED [ 37%]
tests/test_routes/test_video.py::test_post_video_invalid_url_format_no_scheme PASSED [ 50%]
tests/test_routes/test_video.py::test_post_video_no_video_id PASSED    [ 62%]
tests/test_routes/test_video.py::test_post_video_non_youtube_url PASSED [ 75%]
tests/test_routes/test_video.py::test_post_get_video_transcript_success PASSED [ 87%]
tests/test_routes/test_video.py::test_post_get_video_transcript_invalid_video_id PASSED [ 100%]

========================= 8 passed in 3.45s ==========================
```

**설명**:
- 각 테스트의 전체 경로와 이름이 표시됩니다.
- 진행률이 퍼센트로 표시됩니다.
- 테스트 실행 환경 정보가 표시됩니다.

---

#### 3. print 출력 표시 모드 (`-s` 또는 `--capture=no`)

```bash
pytest tests/test_routes/test_video.py -s
```

**출력 예시**:
```
========================= test session starts ==========================
collected 8 items

tests/test_routes/test_video.py::test_post_video_success PASSED

[테스트 결과] POST /api/video (정상 케이스)
요청 URL: https://www.youtube.com/watch?v=dQw4w9WgXcQ
상태 코드: 200
응답 내용: {'video_id': 'dQw4w9WgXcQ', 'status': 'success', 'message': None}
✅ 정상 케이스 테스트 성공!

tests/test_routes/test_video.py::test_post_video_empty_url PASSED

[테스트 결과] POST /api/video (빈 URL)
요청 URL: ''
상태 코드: 422
응답 내용: {'detail': [{'type': 'value_error', 'msg': '...', 'loc': ['body', 'url']}]}
✅ 빈 URL 테스트 성공! (422 에러 정상)

...
========================= 8 passed in 3.45s ==========================
```

**설명**:
- 테스트 코드 내의 `print()` 문 출력이 표시됩니다.
- 디버깅 시 유용합니다.
- 테스트 실행 과정을 상세히 확인할 수 있습니다.

---

#### 4. 상세 출력 + print 출력 (`-v -s`)

```bash
pytest tests/test_routes/test_video.py -v -s
```

**출력 예시**:
```
========================= test session starts ==========================
platform darwin -- Python 3.12.11, pytest-7.4.0, pluggy-1.3.0
rootdir: /Users/datahyeon/Project/youtube-vocabulary-generator
collected 8 items

tests/test_routes/test_video.py::test_post_video_success PASSED        [ 12%]

[테스트 결과] POST /api/video (정상 케이스)
요청 URL: https://www.youtube.com/watch?v=dQw4w9WgXcQ
상태 코드: 200
응답 내용: {'video_id': 'dQw4w9WgXcQ', 'status': 'success', 'message': None}
✅ 정상 케이스 테스트 성공!

tests/test_routes/test_video.py::test_post_video_empty_url PASSED      [ 25%]

[테스트 결과] POST /api/video (빈 URL)
요청 URL: ''
상태 코드: 422
...

========================= 8 passed in 3.45s ==========================
```

**설명**:
- `-v`와 `-s` 옵션을 함께 사용하면 상세한 정보와 print 출력을 모두 볼 수 있습니다.
- 가장 자세한 출력 형식입니다.

---

### 테스트 커버리지 옵션

#### 1. 기본 커버리지 확인

```bash
pytest --cov=app tests/
```

**설명**:
- `--cov=app`: `app/` 폴더의 코드 커버리지를 측정합니다.
- 테스트가 실행된 코드의 비율을 확인할 수 있습니다.

**출력 예시**:
```
========================= test session starts ==========================
collected 15 items

tests/test_main.py::test_app_startup PASSED                      [  6%]
...
========================= 15 passed in 2.34s ==========================

---------- coverage: platform darwin, python 3.12.11 -----------
Name                          Stmts   Miss  Cover
---------------------------------------------------
app/__init__.py                   0      0   100%
app/main.py                      25      2    92%
app/models/schemas.py            45      3    93%
app/routes/video.py              45      5    89%
app/services/validator.py        15      0   100%
app/services/transcript.py        30      8    73%
---------------------------------------------------
TOTAL                           160     18    89%
```

**결과 해석**:
- **Stmts**: 전체 코드 라인 수
- **Miss**: 테스트되지 않은 코드 라인 수
- **Cover**: 커버리지 비율 (퍼센트)
- **TOTAL**: 전체 평균 커버리지 (89%)

---

#### 2. 커버리지 리포트 생성

```bash
pytest --cov=app --cov-report=html tests/
```

**설명**:
- `--cov-report=html`: HTML 형식의 커버리지 리포트를 생성합니다.
- `htmlcov/` 폴더에 리포트가 생성됩니다.

**사용 방법**:
1. 명령어 실행 후 `htmlcov/index.html` 파일을 브라우저로 열기
2. 각 파일별 커버리지와 테스트되지 않은 라인을 시각적으로 확인

**출력 예시**:
```
========================= test session starts ==========================
...
========================= 15 passed in 2.34s ==========================

---------- coverage: platform darwin, python 3.12.11 -----------
Coverage HTML written to dir htmlcov
```

---

#### 3. 커버리지 미만 시 실패

```bash
pytest --cov=app --cov-fail-under=80 tests/
```

**설명**:
- `--cov-fail-under=80`: 커버리지가 80% 미만이면 테스트를 실패로 처리합니다.
- CI/CD 파이프라인에서 최소 커버리지를 보장하는 데 유용합니다.

**출력 예시 (커버리지 80% 미만인 경우)**:
```
========================= test session starts ==========================
...
========================= 15 passed in 2.34s ==========================

---------- coverage: platform darwin, python 3.12.11 -----------
...
TOTAL                           160     18    89%

FAIL Required test coverage of 80% not reached. Total coverage: 75.5%
```

---

### 재실행 옵션

#### 1. 실패한 테스트만 재실행 (`--lf` 또는 `--last-failed`)

```bash
pytest --lf
```

**설명**:
- 이전 실행에서 실패한 테스트만 다시 실행합니다.
- 모든 테스트를 다시 실행하지 않아 시간을 절약할 수 있습니다.

**출력 예시**:
```
========================= test session starts ==========================
collected 15 items / 13 deselected / 2 selected

tests/test_routes/test_video.py::test_post_video_success FAILED        [ 50%]
tests/test_routes/test_video.py::test_post_get_video_transcript_success FAILED [100%]

========================= 2 failed in 1.23s ==========================
```

**설명**:
- 15개 중 2개만 선택되어 실행되었습니다.
- 나머지 13개는 이전에 통과했으므로 건너뛰었습니다.

---

#### 2. 실패한 테스트부터 재실행 (`--ff` 또는 `--failed-first`)

```bash
pytest --ff
```

**설명**:
- 실패한 테스트를 먼저 실행하고, 그 다음 통과한 테스트를 실행합니다.
- 실패한 테스트를 빠르게 확인할 수 있습니다.

**출력 예시**:
```
========================= test session starts ==========================
collected 15 items
run-last-failure: rerun previous 2 failures first.

tests/test_routes/test_video.py::test_post_video_success FAILED        [  6%]
tests/test_routes/test_video.py::test_post_get_video_transcript_success FAILED [ 13%]
tests/test_main.py::test_app_startup PASSED                            [ 20%]
...
```

---

### 기타 유용한 옵션

#### 1. 테스트 실행 시간 표시 (`--durations`)

```bash
pytest --durations=10 tests/
```

**설명**:
- 가장 오래 걸린 테스트 10개를 표시합니다.
- 성능 병목을 찾는 데 유용합니다.

**출력 예시**:
```
========================= test session starts ==========================
...
========================= 15 passed in 2.34s ==========================

========================= slowest 10 test durations ==========================
3.45s setup    tests/test_routes/test_video.py::test_post_get_video_transcript_success
2.12s call     tests/test_routes/test_video.py::test_post_video_success
1.23s call     tests/test_routes/test_video.py::test_post_get_video_transcript_invalid_video_id
...
```

---

#### 2. 테스트 중단 옵션 (`-x` 또는 `--exitfirst`)

```bash
pytest -x
```

**설명**:
- 첫 번째 실패한 테스트에서 즉시 중단합니다.
- 빠르게 실패 원인을 확인할 수 있습니다.

**출력 예시**:
```
========================= test session starts ==========================
collected 15 items

tests/test_main.py::test_app_startup PASSED                      [  6%]
tests/test_main.py::test_health_check PASSED                     [ 13%]
tests/test_routes/test_video.py::test_post_video_success FAILED   [ 20%]

========================= 1 failed, 2 passed in 0.89s ==========================
```

---

#### 3. 최대 실패 수 지정 (`--maxfail`)

```bash
pytest --maxfail=3
```

**설명**:
- 지정한 수만큼 테스트가 실패하면 중단합니다.
- `-x`와 유사하지만 여러 실패를 허용합니다.

**출력 예시**:
```
========================= test session starts ==========================
collected 15 items

tests/test_routes/test_video.py::test_post_video_success FAILED   [  6%]
tests/test_routes/test_video.py::test_post_video_empty_url FAILED [ 13%]
tests/test_routes/test_video.py::test_post_get_video_transcript_success FAILED [ 20%]

========================= 3 failed, 12 passed in 1.45s ==========================
```

---

**[↑ 목차로 돌아가기](#📋-목차)**

---

## 📖 테스트 모듈 작성 가이드

이 섹션은 테스트를 처음 작성하는 개발자도 쉽게 따라할 수 있도록 상세하게 작성되었습니다. 각 단계를 차근차근 따라하면 완벽한 테스트 코드를 작성할 수 있습니다.

### 1. 테스트 파일 생성 및 기본 구조

#### 1.1 테스트 파일 위치 결정

테스트 파일은 `tests/` 폴더 내에서 테스트 대상에 따라 적절한 위치에 생성합니다.

**규칙**:
- **모델/스키마 테스트**: `tests/test_models/test_*.py`
- **라우트/엔드포인트 테스트**: `tests/test_routes/test_*.py`
- **서비스 로직 테스트**: `tests/test_services/test_*.py`
- **앱 메인 테스트**: `tests/test_main.py`

**예시**:
```
tests/
├── test_main.py                    # 앱 메인 테스트
├── test_models/
│   └── test_schemas.py            # 스키마 테스트
├── test_routes/
│   └── test_video.py               # 비디오 엔드포인트 테스트
└── test_services/
    └── test_validator.py          # 검증 서비스 테스트
```

---

#### 1.2 테스트 파일 기본 구조

모든 테스트 파일은 다음 기본 구조를 따릅니다:

```python
"""
테스트 파일 설명

이 파일의 목적과 테스트 대상을 명확히 설명합니다.
"""
import pytest
# 필요한 모듈 import

# ============================================================================
# 테스트 섹션 1: 정상 케이스
# ============================================================================

def test_function_name_1(fixture_name):
    """테스트 함수 설명"""
    # 테스트 코드


# ============================================================================
# 테스트 섹션 2: 에러 케이스
# ============================================================================

def test_function_name_2(fixture_name):
    """테스트 함수 설명"""
    # 테스트 코드
```

**구조 설명**:
1. **파일 상단 docstring**: 파일의 목적과 테스트 대상을 설명
2. **Import 문**: 필요한 모듈 import
3. **섹션 구분**: `# ============================================================================`로 테스트 그룹 구분
4. **테스트 함수**: 각 테스트는 독립적인 함수로 작성

---

### 2. 테스트 함수 네이밍 규칙

테스트 함수 이름은 명확하고 일관성 있게 작성해야 합니다.

#### 2.1 기본 규칙

1. **함수명은 반드시 `test_`로 시작**
   ```python
   # ✅ 올바른 예
   def test_video_url_success():
       pass
   
   # ❌ 잘못된 예
   def video_url_success():  # test_ 접두사 없음
       pass
   ```

2. **테스트하는 기능을 명확히 표현**
   ```python
   # ✅ 좋은 예
   def test_post_video_success():
       """정상적인 YouTube URL로 POST 요청 시 성공 응답 테스트"""
   
   def test_post_video_empty_url():
       """빈 URL로 POST 요청 시 422 에러 테스트"""
   
   # ❌ 나쁜 예
   def test_1():
       """테스트 1"""  # 무엇을 테스트하는지 불명확
   ```

3. **snake_case 사용**
   ```python
   # ✅ 올바른 예
   def test_post_video_success():
       pass
   
   # ❌ 잘못된 예
   def testPostVideoSuccess():  # camelCase 사용
       pass
   ```

---

#### 2.2 네이밍 패턴

일관된 네이밍 패턴을 사용하면 테스트를 이해하기 쉬워집니다.

**패턴 1: `test_{동작}_{조건}_{예상결과}`**
```python
def test_post_video_success():
    """POST 요청, 정상 조건, 성공 결과"""
    pass

def test_post_video_empty_url_error():
    """POST 요청, 빈 URL 조건, 에러 결과"""
    pass
```

**패턴 2: `test_{엔드포인트}_{케이스}`**
```python
def test_post_video_success():
    """POST /api/video 엔드포인트, 정상 케이스"""
    pass

def test_post_video_invalid_url():
    """POST /api/video 엔드포인트, 잘못된 URL 케이스"""
    pass
```

**패턴 3: `test_{함수명}_{케이스}`**
```python
def test_get_transcript_success():
    """get_transcript 함수, 정상 케이스"""
    pass

def test_get_transcript_invalid_video_id():
    """get_transcript 함수, 잘못된 Video ID 케이스"""
    pass
```

---

### 3. 테스트 구조 (AAA 패턴)

모든 테스트는 **AAA 패턴 (Arrange-Act-Assert)**을 따릅니다. 이 패턴은 테스트를 3단계로 명확히 구분하여 가독성을 높입니다.

#### 3.1 AAA 패턴 설명

1. **Arrange (준비)**: 테스트에 필요한 데이터와 환경을 준비
2. **Act (실행)**: 테스트할 코드를 실행
3. **Assert (검증)**: 실행 결과를 검증

#### 3.2 AAA 패턴 예시

**예시 1: 단위 테스트 (스키마 검증)**

```python
def test_video_url_request_success(sample_youtube_url):
    """정상적인 YouTube URL 입력 테스트"""
    # Arrange (준비): fixture에서 정상 URL 가져오기
    url = sample_youtube_url
    
    # Act (실행): VideoUrlRequest 객체 생성
    data = VideoUrlRequests(url=url)
    
    # Assert (검증): 결과 확인
    assert data.url == url
    assert isinstance(data, VideoUrlRequests)
```

**설명**:
- **Arrange**: `sample_youtube_url` fixture에서 정상 URL 가져오기
- **Act**: `VideoUrlRequests` 객체 생성 (테스트할 코드 실행)
- **Assert**: 생성된 객체의 URL이 올바른지 확인

---

**예시 2: API 테스트 (엔드포인트)**

```python
def test_post_video_success(running_server_client: httpx.Client, sample_youtube_url):
    """정상적인 YouTube URL로 POST 요청 시 성공 응답 테스트"""
    # Arrange (준비): fixture에서 정상 URL 가져오기
    url = sample_youtube_url
    
    # Act (실행): POST 요청 보내기
    response = running_server_client.post(
        "/api/video",
        json={"url": url},
        follow_redirects=True
    )
    
    # Assert (검증): 응답 확인
    assert response.status_code == 200
    data = response.json()
    assert "video_id" in data
    assert data["status"] == "success"
```

**설명**:
- **Arrange**: `sample_youtube_url` fixture에서 정상 URL 가져오기
- **Act**: `running_server_client.post()`로 HTTP POST 요청 보내기
- **Assert**: 응답 상태 코드와 응답 데이터 검증

---

**예시 3: 에러 케이스 테스트**

```python
def test_post_video_empty_url(running_server_client: httpx.Client, empty_string):
    """빈 URL로 POST 요청 시 422 에러 테스트"""
    # Arrange (준비): fixture에서 빈 문자열 가져오기
    url = empty_string
    
    # Act (실행): POST 요청 보내기
    response = running_server_client.post(
        "/api/video",
        json={"url": url},
        follow_redirects=True
    )
    
    # Assert (검증): 422 에러 확인
    assert response.status_code == 422
    error_data = response.json()
    assert "detail" in error_data
```

**설명**:
- **Arrange**: `empty_string` fixture에서 빈 문자열 가져오기
- **Act**: 빈 URL로 POST 요청 보내기
- **Assert**: 422 에러와 에러 메시지 확인

---

#### 3.3 AAA 패턴 주의사항

1. **각 단계를 명확히 구분**
   ```python
   # ✅ 좋은 예: 주석으로 단계 구분
   def test_example():
       # Arrange
       url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
       
       # Act
       response = client.post("/api/video", json={"url": url})
       
       # Assert
       assert response.status_code == 200
   ```

2. **한 테스트 함수에 하나의 검증만**
   ```python
   # ✅ 좋은 예: 하나의 검증만 수행
   def test_status_code():
       response = client.post("/api/video", json={"url": url})
       assert response.status_code == 200
   
   def test_response_data():
       response = client.post("/api/video", json={"url": url})
       data = response.json()
       assert "video_id" in data
   
   # ❌ 나쁜 예: 여러 검증을 한 함수에
   def test_everything():
       response = client.post("/api/video", json={"url": url})
    assert response.status_code == 200
    assert "video_id" in response.json()
       assert response.json()["status"] == "success"
       # 너무 많은 검증으로 실패 원인 파악이 어려움
   ```

---

### 4. Docstring 작성 가이드

테스트 함수의 docstring은 테스트의 목적과 검증 내용을 명확히 설명해야 합니다.

#### 4.1 Docstring 구조

```python
def test_function_name(fixture_name):
    """테스트 함수의 간단한 설명
    
    테스트 대상:
        - 어떤 코드/함수/엔드포인트를 테스트하는지
        - 어떤 검증을 수행하는지
    
    사용 예시 (선택사항):
        # 예시 코드
    """
    # 테스트 코드
```

---

#### 4.2 Docstring 예시

**예시 1: 단위 테스트**

```python
def test_video_url_request_success(sample_youtube_url):
    """정상적인 YouTube URL 입력 테스트
    
    테스트 대상:
        - app/models/schemas.py의 VideoUrlRequests 스키마
        - 모든 검증 로직이 통과하는 정상 케이스
    
    검증 내용:
        - 정상적인 YouTube URL로 객체 생성 시 에러 없이 생성됨
        - 생성된 객체의 url 속성이 입력값과 일치함
    """
    # 테스트 코드
```

---

**예시 2: API 테스트**

```python
def test_post_video_success(running_server_client: httpx.Client, sample_youtube_url):
    """정상적인 YouTube URL로 POST 요청 시 성공 응답 테스트
    
    테스트 대상:
        - app/routes/video.py의 POST /api/video 엔드포인트
        - 정상적인 YouTube URL 입력 시 Video ID 반환 확인
    
    검증 내용:
        - 상태 코드 200 반환
        - 응답에 video_id, status 필드 포함
        - status가 "success"
        - video_id가 올바른 값
    """
    # 테스트 코드
```

---

**예시 3: 에러 케이스 테스트**

```python
def test_post_video_empty_url(running_server_client: httpx.Client, empty_string):
    """빈 URL로 POST 요청 시 422 에러 테스트
    
    테스트 대상:
        - app/models/schemas.py의 validate_url_not_empty 검증
        - 스키마 검증 실패 시 422 에러 반환 확인
    
    검증 내용:
        - 상태 코드 422 반환
        - 응답에 detail 필드 포함 (에러 메시지)
    """
    # 테스트 코드
```

---

### 5. Fixture 사용 방법

Fixture는 테스트에 필요한 데이터나 객체를 제공하는 함수입니다. pytest가 자동으로 fixture를 주입해줍니다.

#### 5.1 Fixture 사용 기본 방법

**방법 1: 함수 매개변수로 fixture 이름 지정**

```python
def test_example(sample_youtube_url):
    """fixture를 함수 매개변수로 받기"""
    url = sample_youtube_url  # fixture 값 사용
    # 테스트 코드
```

**설명**:
- 함수 매개변수 이름이 fixture 이름과 일치하면 pytest가 자동으로 주입합니다.
- `sample_youtube_url` fixture가 자동으로 호출되어 값을 반환합니다.

---

**방법 2: 여러 fixture 사용**

```python
def test_example(running_server_client, sample_youtube_url, sample_video_id):
    """여러 fixture를 동시에 사용"""
    # running_server_client fixture 사용
    response = running_server_client.post(
        "/api/video",
        json={"url": sample_youtube_url}  # sample_youtube_url fixture 사용
    )
    # sample_video_id fixture 사용
    video_id = sample_video_id
    # 테스트 코드
```

**설명**:
- 여러 fixture를 함수 매개변수로 나열하면 모두 자동으로 주입됩니다.
- fixture 간 의존성이 있어도 pytest가 자동으로 해결합니다.

---

#### 5.2 Fixture 사용 예시

**예시 1: 단위 테스트에서 fixture 사용**

```python
def test_video_url_request_success(sample_youtube_url):
    """정상적인 YouTube URL 입력 테스트"""
    # Arrange: fixture에서 정상 URL 가져오기
    url = sample_youtube_url  # "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    # Act: VideoUrlRequest 객체 생성
    data = VideoUrlRequests(url=url)
    
    # Assert: 결과 확인
    assert data.url == url
```

---

**예시 2: API 테스트에서 fixture 사용**

```python
def test_post_video_success(running_server_client: httpx.Client, sample_youtube_url):
    """정상적인 YouTube URL로 POST 요청 시 성공 응답 테스트"""
    # Arrange: fixture에서 정상 URL 가져오기
    url = sample_youtube_url
    
    # Act: 실행 중인 서버에 POST 요청 보내기
    response = running_server_client.post(
        "/api/video",
        json={"url": url},
        follow_redirects=True
    )
    
    # Assert: 응답 확인
    assert response.status_code == 200
```

---

#### 5.3 Fixture 사용 주의사항

1. **Fixture 이름은 정확히 일치해야 함**
```python
   # ✅ 올바른 예
   def test_example(sample_youtube_url):  # fixture 이름과 일치
       pass
   
   # ❌ 잘못된 예
   def test_example(sample_url):  # fixture 이름과 불일치 (에러 발생)
       pass
   ```

2. **Fixture는 conftest.py에 정의되어 있어야 함**
   - `tests/conftest.py`: 전체 공통 fixture
   - `tests/test_models/conftest.py`: 모델 테스트 전용 fixture
   - `tests/test_routes/conftest.py`: 라우트 테스트 전용 fixture

---

### 6. Assertion 작성 가이드

Assertion은 테스트의 핵심입니다. 명확하고 구체적인 assertion을 작성해야 합니다.

#### 6.1 기본 Assertion

```python
# 값 비교
assert response.status_code == 200
assert data["status"] == "success"

# 포함 여부 확인
assert "video_id" in data
assert "error" not in data

# 타입 확인
assert isinstance(data, dict)
assert isinstance(data["video_id"], str)

# 길이 확인
assert len(data["transcript"]) > 0
assert len(error_list) == 3
```

---

#### 6.2 에러 케이스 Assertion

```python
# 예외 발생 확인
with pytest.raises(ValidationError) as exc_info:
    VideoUrlRequests(url="")

# 예외 메시지 확인
errors = exc_info.value.errors()
assert len(errors) > 0
assert errors[0]["type"] == "value_error"
assert "비어있을 수 없습니다" in str(errors[0]["msg"])
```

---

#### 6.3 HTTP 응답 Assertion

```python
# 상태 코드 확인
assert response.status_code == 200
assert response.status_code == 422
assert response.status_code == 400

# 응답 형식 확인
assert response.headers.get("content-type", "").startswith("application/json")

# 응답 데이터 확인
data = response.json()
assert "video_id" in data
assert data["status"] == "success"
assert data["video_id"] == "dQw4w9WgXcQ"
```

---

### 7. 테스트 파일 작성 완전 예시

이제 모든 가이드를 종합하여 완전한 테스트 파일을 작성하는 예시를 보여드립니다.

#### 예시: 새로운 엔드포인트 테스트 작성

**시나리오**: `POST /api/video/{video_id}/transcript` 엔드포인트 테스트 작성

**1단계: 파일 생성**

`tests/test_routes/test_video.py` 파일에 추가 (또는 새 파일 생성)

**2단계: 기본 구조 작성**

```python
"""
비디오 라우트 엔드포인트 테스트

이 테스트는 실행 중인 서버를 대상으로 합니다.
사용법:
    1. 터미널에서 서버 실행: uvicorn app.main:app --reload
    2. 다른 터미널에서 테스트 실행: pytest tests/test_routes/test_video.py -v -s
"""
import pytest
import httpx

# ============================================================================
# POST /api/video/{video_id}/transcript 엔드포인트 테스트
# ============================================================================
```

**3단계: 정상 케이스 테스트 작성**

```python
def test_post_get_video_transcript_success(
    running_server_client: httpx.Client, 
    sample_video_id
):
    """정상적인 Video ID로 자막 추출 요청 시 성공 응답 테스트
    
    테스트 대상:
        - app/routes/video.py의 POST /api/video/{video_id}/transcript 엔드포인트
        - 자막이 있는 영상으로 자막 추출 성공 확인
    
    검증 내용:
        - 상태 코드 200 반환
        - 응답에 video_id, transcript, status, language 필드 포함
        - status가 "success"
        - transcript에 자막 텍스트 존재
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
    assert len(data["transcript"]) > 0  # 자막 텍스트가 있는지 확인
    print("✅ 정상 케이스 테스트 성공!")
```

**4단계: 에러 케이스 테스트 작성**

```python
def test_post_get_video_transcript_invalid_video_id(
    running_server_client: httpx.Client,
    invalid_video_id
):
    """존재하지 않는 Video ID로 자막 추출 요청 시 에러 응답 테스트
    
    테스트 대상:
        - app/routes/video.py의 POST /api/video/{video_id}/transcript 엔드포인트
        - app/services/transcript.py의 get_transcript 함수
        - 존재하지 않는 영상 ID 입력 시 400 에러 반환 확인
    
    검증 내용:
        - 상태 코드 400 반환
        - 응답에 detail 필드 포함 (에러 메시지)
        - 에러 메시지에 Video ID 포함
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
    assert video_id in error_data["detail"]  # 에러 메시지에 Video ID가 포함되어 있는지 확인
    print("✅ 존재하지 않는 Video ID 테스트 성공! (400 에러 정상)")
```

**5단계: 테스트 실행 및 확인**

```bash
# 터미널 1: 서버 실행
uvicorn app.main:app --reload

# 터미널 2: 테스트 실행
pytest tests/test_routes/test_video.py::test_post_get_video_transcript_success -v -s
```

---

**[↑ 목차로 돌아가기](#📋-목차)**

---

## 8. 테스트 디버깅 가이드

테스트가 실패했을 때 원인을 찾는 방법을 상세히 설명합니다.

#### 8.1 실패한 테스트 분석 방법

**1단계: 에러 메시지 확인**

```bash
pytest tests/test_routes/test_video.py::test_post_video_success -v
```

**출력 예시 (실패한 경우)**:
```
tests/test_routes/test_video.py::test_post_video_success FAILED

================================= FAILURES =================================
_________________________ test_post_video_success __________________________

    def test_post_video_success(running_server_client, sample_youtube_url):
        response = running_server_client.post(
            "/api/video",
            json={"url": url},
            follow_redirects=True
        )
>       assert response.status_code == 200
E       AssertionError: assert 422 == 200
E        +  where 422 = <Response [422 Unprocessable Entity]>.status_code

tests/test_routes/test_video.py:50: AssertionError
```

**분석 방법**:
- `AssertionError: assert 422 == 200`: 예상한 상태 코드(200)와 실제 상태 코드(422)가 다름
- `422 Unprocessable Entity`: 스키마 검증 실패를 의미
- 실패한 라인: `tests/test_routes/test_video.py:50` - 50번 줄에서 실패

**2단계: 실제 응답 내용 확인**

테스트 코드에 디버깅용 print 문을 추가합니다:

```python
def test_post_video_success(running_server_client, sample_youtube_url):
    response = running_server_client.post(
        "/api/video",
        json={"url": sample_youtube_url},
        follow_redirects=True
    )
    
    # 디버깅: 실제 응답 내용 출력
    print(f"\n[디버깅 정보]")
    print(f"상태 코드: {response.status_code}")
    print(f"응답 헤더: {response.headers}")
    print(f"응답 내용: {response.json()}")
    
    assert response.status_code == 200
```

**실행 방법**:
```bash
pytest tests/test_routes/test_video.py::test_post_video_success -v -s
```

**출력 예시**:
```
[디버깅 정보]
상태 코드: 422
응답 헤더: {'content-type': 'application/json', ...}
응답 내용: {'detail': [{'type': 'value_error', 'msg': '...', 'loc': ['body', 'url']}]}
```

**3단계: 서버 로그 확인**

서버가 실행 중인 터미널에서 로그를 확인합니다:

```
INFO:     127.0.0.1:53029 - "POST /api/video HTTP/1.1" 422 Unprocessable Entity
2025-11-17 10:05:20 [ERROR] error: 요청 처리 중 오류 발생: POST /api/video - ...
```

---

#### 8.2 일반적인 실패 원인 및 해결 방법

**문제 1: 서버가 실행되지 않음**

**증상**:
```
ConnectionRefusedError: [Errno 61] Connection refused
```

**원인**: `running_server_client` fixture를 사용하는 테스트는 서버가 실행 중이어야 합니다.

**해결 방법**:
```bash
# 터미널 1에서 서버 실행
uvicorn app.main:app --reload

# 서버가 정상적으로 실행되었는지 확인
curl http://localhost:8000/health
```

---

**문제 2: Fixture 이름 오타**

**증상**:
```
fixture 'sample_youtube_ur' not found
available fixtures: sample_youtube_url, empty_string, ...
```

**원인**: 함수 매개변수 이름이 fixture 이름과 일치하지 않음

**해결 방법**:
1. `conftest.py`에서 fixture 이름 확인
2. 함수 매개변수 이름을 fixture 이름과 정확히 일치시킴

```python
# ✅ 올바른 예
def test_example(sample_youtube_url):  # fixture 이름과 일치
    pass

# ❌ 잘못된 예
def test_example(sample_youtube_ur):  # 오타
    pass
```

---

**문제 3: 응답 형식이 예상과 다름**

**증상**:
```
KeyError: 'video_id'
```

**원인**: 응답 구조가 예상과 다름

**해결 방법**:
```python
# 실제 응답 내용 확인
print(f"응답 내용: {response.json()}")

# 응답 구조 확인
data = response.json()
print(f"응답 키: {list(data.keys())}")

# 안전하게 접근
if "video_id" in data:
    assert data["video_id"] == "expected"
else:
    print(f"예상하지 못한 응답 구조: {data}")
```

---

**문제 4: 타임아웃 에러**

**증상**:
```
httpx.ReadTimeout: The read operation timed out
```

**원인**: 서버 응답 시간이 너무 오래 걸림

**해결 방법**:
1. `conftest.py`의 `running_server_client` fixture에서 timeout 값 증가
2. 서버 응답 시간 확인

```python
# conftest.py 수정
@pytest.fixture
def running_server_client():
    base_url = "http://localhost:8000"
    with httpx.Client(base_url=base_url, timeout=30.0) as client:  # 10초 → 30초
        yield client
```

---

**문제 5: 테스트가 때때로 실패함 (Flaky Test)**

**증상**: 같은 테스트가 때때로 통과하고 때때로 실패함

**원인**:
- 비결정적 동작 (랜덤, 시간 등)
- 외부 의존성 (네트워크, API 등)
- 테스트 간 의존성

**해결 방법**:
1. Mock 사용: 외부 의존성을 Mock으로 대체
2. 고정된 값 사용: 랜덤 값 대신 고정된 값 사용
3. 테스트 독립성 확인: 각 테스트가 독립적으로 실행 가능한지 확인

```python
# ❌ 나쁜 예: 랜덤 값 사용
import random
def test_random():
    value = random.randint(1, 100)
    assert value > 50  # 때때로 실패

# ✅ 좋은 예: 고정된 값 사용
def test_fixed():
    value = 75  # 고정된 값
    assert value > 50  # 항상 통과
```

---

**[↑ 목차로 돌아가기](#📋-목차)**

---

## 9. 테스트 작성 시 주의사항

테스트를 작성할 때 반드시 지켜야 할 중요한 원칙들입니다.

#### 9.1 테스트 독립성 (Test Independence)

**원칙**: 각 테스트는 다른 테스트에 의존하지 않아야 합니다.

**✅ 좋은 예**:
```python
def test_1(sample_youtube_url):
    """독립적인 테스트 1"""
    data = VideoUrlRequests(url=sample_youtube_url)
    assert data.url == sample_youtube_url

def test_2(sample_youtube_url):
    """독립적인 테스트 2 (test_1과 무관)"""
    data = VideoUrlRequests(url=sample_youtube_url)
    assert isinstance(data, VideoUrlRequests)
```

**설명**:
- `test_1`과 `test_2`는 서로 독립적
- 어떤 순서로 실행되어도 결과가 같음
- 하나가 실패해도 다른 하나에 영향 없음

**❌ 나쁜 예**:
```python
# 전역 변수 사용 (테스트 간 의존성 발생)
test_data = None

def test_1():
    global test_data
    test_data = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    assert test_data is not None

def test_2():
    # test_1이 먼저 실행되어야 함 (의존성 발생)
    assert test_data is not None  # test_1이 실행되지 않으면 실패
```

**문제점**:
- `test_2`가 `test_1`보다 먼저 실행되면 실패
- 테스트 실행 순서에 의존적
- 테스트 간 결합도가 높음

---

#### 9.2 테스트 재현 가능성 (Test Reproducibility)

**원칙**: 같은 입력에 대해 항상 같은 결과가 나와야 합니다.

**✅ 좋은 예**:
```python
def test_video_url_request_success(sample_youtube_url):
    """항상 같은 결과를 반환하는 테스트"""
    data = VideoUrlRequests(url=sample_youtube_url)
    assert data.url == sample_youtube_url  # 항상 True
```

**❌ 나쁜 예**:
```python
import random
import time

def test_random():
    """랜덤 값을 사용하는 테스트 (재현 불가능)"""
    value = random.randint(1, 100)
    assert value > 50  # 때때로 실패할 수 있음

def test_time():
    """시간에 의존하는 테스트 (재현 불가능)"""
    current_time = time.time()
    assert current_time > 1000000000  # 시간이 지나면 실패할 수 있음
```

---

#### 9.3 테스트 속도 (Test Speed)

**원칙**: 테스트는 빠르게 실행되어야 합니다.

**✅ 좋은 예**:
```python
def test_fast():
    """빠른 테스트 (로컬에서 실행, 외부 의존성 없음)"""
    data = VideoUrlRequests(url="https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    assert data.url is not None
```

**❌ 나쁜 예**:
```python
import time

def test_slow():
    """느린 테스트 (불필요한 대기)"""
    time.sleep(5)  # 불필요한 5초 대기
    assert True
```

**개선 방법**:
- 불필요한 대기 시간 제거
- 외부 API 호출은 Mock으로 대체
- 필요한 경우에만 실제 API 호출

---

#### 9.4 명확한 실패 메시지 (Clear Failure Messages)

**원칙**: 테스트가 실패했을 때 무엇이 잘못되었는지 알 수 있어야 합니다.

**✅ 좋은 예**:
```python
def test_with_clear_message():
    """명확한 에러 메시지"""
    response = client.post("/api/video", json={"url": ""})
    assert response.status_code == 422, \
        f"예상: 422 (Unprocessable Entity), 실제: {response.status_code}. " \
        f"응답 내용: {response.json()}"
```

**실패 시 출력**:
```
AssertionError: 예상: 422 (Unprocessable Entity), 실제: 200. 응답 내용: {'video_id': '...'}
```

**❌ 나쁜 예**:
```python
def test_without_message():
    """에러 메시지 없음"""
    response = client.post("/api/video", json={"url": ""})
    assert response.status_code == 422  # 왜 실패했는지 불명확
```

**실패 시 출력**:
```
AssertionError: assert 200 == 422
```

---

**[↑ 목차로 돌아가기](#📋-목차)**

---

## 10. 테스트 모범 사례

프로젝트에서 권장하는 테스트 작성 방법과 목표입니다.

#### 10.1 테스트 커버리지 목표

**목표 커버리지**:
- **전체 코드**: 80% 이상
- **핵심 비즈니스 로직**: 100% 커버리지 목표
- **에러 핸들링**: 모든 에러 케이스 테스트

**커버리지 확인 방법**:
```bash
# 커버리지 확인
pytest --cov=app --cov-report=term tests/

# HTML 리포트 생성
pytest --cov=app --cov-report=html tests/
# → htmlcov/index.html 파일 열기
```

---

#### 10.2 테스트 우선순위

**높은 우선순위** (반드시 테스트):
- 핵심 비즈니스 로직
- 에러 핸들링
- 보안 관련 검증

**중간 우선순위** (가능하면 테스트):
- 일반적인 사용 케이스
- API 엔드포인트

**낮은 우선순위** (선택적):
- 엣지 케이스
- 최적화 관련 코드

---

#### 10.3 테스트 리팩토링

**원칙**: 테스트 코드도 프로덕션 코드처럼 리팩토링해야 합니다.

**중복 제거 예시**:

**❌ 나쁜 예: 중복된 코드**
```python
def test_1():
    response = client.post(
        "/api/video",
        json={"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}
    )
    assert response.status_code == 200

def test_2():
    response = client.post(
        "/api/video",
        json={"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"}
    )
    assert "video_id" in response.json()
```

**✅ 좋은 예: 헬퍼 함수 사용**
```python
def make_video_request(url):
    """공통 요청 함수"""
    return client.post("/api/video", json={"url": url})

def test_status_code():
    """상태 코드만 테스트"""
    response = make_video_request("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    assert response.status_code == 200

def test_response_data():
    """응답 데이터만 테스트"""
    response = make_video_request("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    assert "video_id" in response.json()
```

---

**[↑ 목차로 돌아가기](#📋-목차)**

---

## 11. 테스트 실행 체크리스트

테스트를 작성하고 실행하기 전에 확인해야 할 항목들을 정리합니다.

### 11.1 테스트 작성 후 체크리스트

**코드 품질**:
- [ ] 테스트 함수명이 `test_`로 시작하는가?
- [ ] 테스트 함수에 docstring이 있는가?
- [ ] AAA 패턴을 따르고 있는가?
- [ ] Fixture를 올바르게 사용하고 있는가?
- [ ] Assertion이 명확하고 구체적인가?

**테스트 커버리지**:
- [ ] 정상 케이스를 테스트하는가?
- [ ] 에러 케이스를 테스트하는가?
- [ ] 엣지 케이스를 고려했는가?

**테스트 품질**:
- [ ] 테스트가 독립적으로 실행 가능한가?
- [ ] 테스트가 빠르게 실행되는가?
- [ ] 테스트가 재현 가능한가?

---

### 11.2 테스트 실행 전 체크리스트

**실행 중인 서버를 대상으로 하는 테스트의 경우**:
- [ ] 서버가 실행 중인가? (`uvicorn app.main:app --reload`)
- [ ] 서버가 올바른 포트(8000)에서 실행 중인가?
- [ ] 서버가 정상적으로 응답하는가? (`curl http://localhost:8000/health`)

**일반 테스트의 경우**:
- [ ] 필요한 의존성이 설치되어 있는가? (`pip install -r requirements.txt`)
- [ ] 환경 변수가 올바르게 설정되어 있는가?
- [ ] 테스트 데이터베이스가 준비되어 있는가? (필요한 경우)

---

**[↑ 목차로 돌아가기](#📋-목차)**

---

## 12. 문제 해결 FAQ

자주 발생하는 문제와 해결 방법을 상세히 정리합니다.

### Q1: "fixture not found" 에러가 발생합니다.

**에러 메시지**:
```
fixture 'sample_youtube_url' not found
available fixtures: client, running_server_client, ...
```

**원인**:
- Fixture 이름 오타
- Fixture가 정의되지 않은 `conftest.py`에 있음
- `conftest.py` 파일이 올바른 위치에 없음

**해결 방법**:

1. **Fixture 이름 확인**
```bash
   # 사용 가능한 fixture 목록 확인
   pytest --fixtures tests/test_routes/test_video.py
   ```

2. **conftest.py 위치 확인**
   - `tests/conftest.py`: 전체 공통 fixture
   - `tests/test_routes/conftest.py`: 라우트 테스트 전용 fixture
   - `tests/test_models/conftest.py`: 모델 테스트 전용 fixture

3. **함수 매개변수 이름 확인**
   ```python
   # ✅ 올바른 예
   def test_example(sample_youtube_url):  # fixture 이름과 정확히 일치
       pass
   
   # ❌ 잘못된 예
   def test_example(sample_url):  # fixture 이름과 불일치
       pass
   ```

---

### Q2: 테스트가 너무 느립니다.

**원인**:
- 외부 API 호출
- 불필요한 대기 시간
- 너무 많은 테스트를 한 번에 실행

**해결 방법**:

1. **Mock 사용**: 외부 API 호출을 Mock으로 대체
```python
   from unittest.mock import patch
   
   @patch('app.services.transcript.YouTubeTranscriptApi')
   def test_fast(mock_api):
       """Mock을 사용한 빠른 테스트"""
       mock_api.return_value.fetch.return_value.to_raw_data.return_value = [
           {"text": "Hello", "start": 0.0, "duration": 2.0}
       ]
       result = get_transcript("dQw4w9WgXcQ")
       assert len(result) > 0
   ```

2. **특정 테스트만 실행**
   ```bash
   # 특정 테스트만 실행
   pytest tests/test_routes/test_video.py::test_post_video_success
   ```

3. **병렬 실행** (pytest-xdist 필요)
   ```bash
   pip install pytest-xdist
   pytest -n auto  # CPU 코어 수만큼 병렬 실행
   ```

---

### Q3: 서버 연결 에러가 발생합니다.

**에러 메시지**:
```
ConnectionRefusedError: [Errno 61] Connection refused
```

**원인**:
- 서버가 실행되지 않음
- 잘못된 포트 번호
- 방화벽 문제

**해결 방법**:

1. **서버 실행 확인**
   ```bash
   # 터미널 1에서 서버 실행
   uvicorn app.main:app --reload
   
   # 서버가 정상적으로 실행되었는지 확인
   curl http://localhost:8000/health
   ```

2. **포트 확인**
   ```python
   # conftest.py에서 포트 확인
   base_url = "http://localhost:8000"  # 포트 번호 확인
   ```

3. **서버 상태 확인**
   ```bash
   # 서버가 실행 중인지 확인
   lsof -i :8000
   
   # 또는
   netstat -an | grep 8000
   ```

---

### Q4: 테스트가 때때로 실패합니다 (Flaky Test).

**증상**: 같은 테스트가 때때로 통과하고 때때로 실패함

**원인**:
- 비결정적 동작 (랜덤, 시간 등)
- 외부 의존성 (네트워크, API 등)
- 테스트 간 의존성

**해결 방법**:

1. **Mock 사용**: 외부 의존성을 Mock으로 대체
   ```python
   # ❌ 나쁜 예: 실제 API 호출
   def test_flaky():
       transcript = get_transcript("dQw4w9WgXcQ")  # 네트워크 의존
       assert len(transcript) > 0
   
   # ✅ 좋은 예: Mock 사용
   @patch('app.services.transcript.YouTubeTranscriptApi')
   def test_stable(mock_api):
       mock_api.return_value.fetch.return_value.to_raw_data.return_value = [
           {"text": "Hello", "start": 0.0, "duration": 2.0}
       ]
       transcript = get_transcript("dQw4w9WgXcQ")
       assert len(transcript) > 0
   ```

2. **고정된 값 사용**: 랜덤 값 대신 고정된 값 사용
   ```python
   # ❌ 나쁜 예
   import random
   def test_random():
       value = random.randint(1, 100)
       assert value > 50
   
   # ✅ 좋은 예
   def test_fixed():
       value = 75  # 고정된 값
       assert value > 50
   ```

3. **테스트 독립성 확인**: 각 테스트가 독립적으로 실행 가능한지 확인

---

### Q5: 커버리지가 낮습니다.

**원인**:
- 테스트되지 않은 코드가 많음
- 에러 핸들링 코드가 테스트되지 않음

**해결 방법**:

1. **커버리지 리포트 확인**
   ```bash
   # HTML 리포트 생성
   pytest --cov=app --cov-report=html tests/
   
   # htmlcov/index.html 파일을 브라우저로 열기
   open htmlcov/index.html
   ```

2. **테스트되지 않은 라인 확인**
   - HTML 리포트에서 빨간색으로 표시된 라인 확인
   - 해당 라인을 테스트하는 케이스 추가

3. **누락된 테스트 케이스 추가**
   - 정상 케이스: 모든 함수의 정상 동작 테스트
   - 에러 케이스: 모든 예외 상황 테스트
   - 엣지 케이스: 경계값 테스트

---

**[↑ 목차로 돌아가기](#📋-목차)**

---

## 🔗 참고 자료

테스트 작성 및 pytest 사용에 도움이 되는 공식 문서와 학습 자료입니다.

### 공식 문서

- **[FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)**
  - FastAPI 공식 테스트 가이드
  - TestClient 사용법
  - HTTP 요청 테스트 방법
  - 비동기 테스트 작성법

- **[pytest Documentation](https://docs.pytest.org/)**
  - pytest 공식 문서
  - Fixture 사용법
  - 마커 및 플러그인
  - 고급 기능

- **[pytest-asyncio](https://pytest-asyncio.readthedocs.io/)**
  - 비동기 테스트 작성 가이드
  - async/await 테스트 방법
  - 비동기 fixture 사용법

- **[httpx Documentation](https://www.python-httpx.org/)**
  - httpx HTTP 클라이언트 문서
  - HTTP 요청/응답 처리
  - 비동기 HTTP 클라이언트

---

### 추가 학습 자료

- **Test-Driven Development (TDD)**: 테스트 주도 개발 방법론
- **Mocking in Python**: Mock 사용법 및 패턴
- **pytest Best Practices**: 테스트 작성 모범 사례
- **Python Testing**: Python 테스트 전반에 대한 가이드

---

## 📌 마무리

이 문서는 FastAPI 프로젝트의 테스트 작성과 실행에 대한 완전한 가이드입니다. 

### 핵심 요약

1. **테스트 종류**: 단위 테스트, 통합 테스트, API 테스트 (E2E)
2. **테스트 구조**: AAA 패턴 (Arrange-Act-Assert)
3. **Fixture 사용**: `conftest.py`에 정의된 fixture 자동 주입
4. **테스트 실행**: `pytest` 명령어와 다양한 옵션 활용
5. **테스트 작성**: 명확한 네이밍, 상세한 docstring, 독립적인 테스트

### 다음 단계

- 새로운 엔드포인트 추가 시 해당 엔드포인트 테스트 작성
- 새로운 서비스 함수 추가 시 단위 테스트 작성
- 커버리지 목표(80%) 달성을 위한 지속적인 테스트 추가
- 이 문서를 프로젝트가 진행됨에 따라 계속 업데이트

---

**문서 버전**: 2.0  
**최종 업데이트**: 2025-11-17  
**작성자**: 프로젝트 팀

---

> 💡 **팁**: 이 문서는 프로젝트가 진행됨에 따라 계속 업데이트됩니다. 새로운 테스트 파일이 추가되거나 테스트 방법이 변경되면 이 문서도 함께 업데이트해주세요.  
>   
> 📝 **피드백**: 이 문서에 대한 개선 사항이나 추가할 내용이 있으면 언제든지 제안해주세요!