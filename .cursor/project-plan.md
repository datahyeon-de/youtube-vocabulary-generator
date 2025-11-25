# 1. 프로젝트 개요

- **목적**: 유튜브 영상 자막을 기반으로 도메인별 영어 단어장을 자동 생성하는 FastAPI 기반 서비스 구축
- **주요 기능**:
  - 유튜브 링크 입력 및 검증
  - 자막 데이터 추출 및 전처리
  - LLM을 활용한 단어 선별과 한국어 뜻 생성
  - 단어장 생성 및 제공 API
- **기술 스택**: Python, FastAPI, Pydantic, Starlette Middleware, pytest, youtube-transcript-api, transformers, LLM API(도입 예정)
- **주 사용자**: 유튜브 학습용 단어장을 빠르게 확보하고 싶은 학습자 및 교육자

# 2. 주요 목표 및 산출물

1. 신뢰성 있는 YouTube URL 검증 및 Video ID 추출 모듈
2. 요청/응답 전 과정을 기록하는 로깅 인프라
3. YouTube Transcript API를 활용한 자막 추출 서비스
4. LLM 기반 단어 선별 및 한-영 단어장 생성 로직
5. 단어장 전달을 위한 최종 API 및 테스트 스위트

# 3. Phase & Task 세부 계획

## ✅ Phase 1: 프로젝트 초기 설정
- ✅ FastAPI 프로젝트 구조화
- ✅ 테스트 환경 및 pytest 설정
- ✅ 기본 의존성 및 설정 파일 정리

## ✅ Phase 2: FastAPI 서버 및 입력 검증 시스템
- ✅ `POST /api/video` 엔드포인트 구현
- ✅ YouTube URL 검증 및 Video ID 추출 로직 작성
- ✅ 요청/응답 예외 처리 (422, 400)
- ✅ 관련 테스트 케이스 작성

## ✅ 추가 작업: 로깅 미들웨어 구축
- ✅ 로깅 설정 모듈 (`app/core/logging.py`) 구성
- ✅ 요청/응답 로깅 미들웨어 작성 및 등록
- ✅ 로그 파일 분리 및 로테이션 설정

## ✅ Phase 3: 자막 추출 서비스
- ✅ `youtube-transcript-api` 의존성 추가 및 관리
- ✅ `transformers` 라이브러리 추가 (`requirements.txt`) - 토큰화 및 청크 생성을 위함
- ✅ `TranscriptResponse` 스키마 정의 (`app/models/schemas.py`)
  - `transcript` 필드 타입: `str` → `List[Dict]`로 변경 (청크 기반 응답)
- ✅ `get_transcript(video_id)` 서비스 구현 (`app/services/transcript.py`)
  - 토큰화 기능 추가 (`count_tokens` 함수)
  - 청크 생성 기능 추가 (`create_chunks` 함수) - 2000 토큰 단위로 자막을 청크로 분할
  - 반환 타입: `str` → `List[dict]`로 변경 (각 청크는 `text`, `token_count`, `segment_range` 키 포함)
- ✅ `POST /api/video/{video_id}/transcript` 엔드포인트 추가
- ✅ 자막 미존재, 비공개 처리 등 예외 핸들링
- ✅ 테스트 파일에 청크 구조 검증 추가 (`tests/test_routes/test_video.py`)
  - 각 청크가 딕셔너리인지 확인
  - 각 청크에 필수 키(`text`, `token_count`, `segment_range`) 존재 여부 확인
- ✅ 기본 수동 테스트 절차 정리

## ⏳ Phase 4: LLM 처리 서버 구축
- ✅ vLLM 서버 연동 설정
  - vLLM 서버 엔드포인트 설정 (http://tc-server-gpu:8000/v1/chat/completions)
  - 모델명 설정 ("Qwen/Qwen2.5-14B-Instruct-AWQ")
  - HTTP 클라이언트 구성 (httpx 비동기 사용)
  - 환경 변수 관리 (서버 URL, 타임아웃 등)
  - 인증 불필요 (내부 VPN 대역대)
- ✅ LLM 설정 모듈 구성
  - LLM 설정 모듈 생성 (`app/core/config.py`에 추가)
  - vLLM 서버 URL, 모델명, 타임아웃 설정
  - 재시도 로직 설정 (최대 재시도 횟수, 백오프 전략)
- ✅ LLM 클라이언트 모듈 구현
  - vLLM API 클라이언트 구현 (`app/services/llm/client.py`)
  - OpenAI 호환 API 형식 지원 (`/v1/chat/completions`)
  - 비동기 병렬 요청 처리 (asyncio 사용)
  - JSON 응답 파싱 및 검증
- ✅ 프롬프트 템플릿 모듈 구현
  - 프롬프트 템플릿 관리 모듈 (`app/services/llm/prompts.py`)
  - 단어 추출 프롬프트 템플릿 (1단계, 한국어)
  - 숙어 추출 프롬프트 템플릿 (1단계, 한국어)
  - 단어 상세 정보 프롬프트 템플릿 (2단계: 품사, 동의어, 예문, 한국어)
  - 숙어 예문 생성 프롬프트 템플릿 (2단계: 예문, 한국어)
  - JSON 응답 형식 명시 (각 프롬프트에 포함)
- ⏳ 1단계: 단어 및 숙어 추출 로직 구현 (진행 중)
  - ✅ 단어 추출 함수 구현 (`app/services/llm/extract_words.py`)
    - 입력: 청크 텍스트 리스트, video_id
    - 프롬프트: 단어 추출용 (모든 단어 추출, 문맥상 사용되는 뜻 최대 2개, 품사 포함)
    - 출력: {videoId: video_id, result: {단어: {품사: "n", 뜻: [뜻1, 뜻2]}, ...}}
    - 구현 완료: 청크별 병렬 처리 (asyncio.gather), 결과 병합, 에러 핸들링, 로깅, 부분 실패 허용
    - 내부 헬퍼 함수 `_extract_words_from_single_chunk` 구현
  - ◻️ 숙어 추출 함수 구현 (`app/services/llm/extract_phrases.py`)
    - 입력: 청크 텍스트 리스트, video_id
    - 프롬프트: 숙어 추출용 (idiom, phrasal verb, collocation 기준)
    - 출력: {videoId: video_id, result: {숙어: 뜻, ...}}
  - ◻️ 병렬 처리 로직 (청크별로 단어/숙어 추출 프롬프트 동시 전송)
- ◻️ 2단계: 단어 및 숙어 상세 정보 생성 로직 구현
  - 단어 상세 정보 생성 함수 구현 (`app/services/llm/enrich_words.py`)
    - 입력: 1단계 단어 추출 결과, 원본 청크 텍스트
    - 프롬프트: 품사, 동의어, 예문 생성용 (한국어)
    - 출력: {videoId: video_id, result: {단어: {품사: 품사, 동의어: [동의어1, 동의어2], 예문: 예문}, ...}}
  - 숙어 예문 생성 함수 구현 (`app/services/llm/enrich_phrases.py`)
    - 입력: 1단계 숙어 추출 결과, 원본 청크 텍스트
    - 프롬프트: 예문 생성용 (한국어)
    - 출력: {videoId: video_id, result: {숙어: {예문: 예문}, ...}}
- ◻️ 3단계: 결과 병합 및 통합 로직 구현
  - 결과 병합 함수 구현 (`app/services/llm/merge_results.py`)
    - 입력: 모든 청크의 2단계 결과들
    - 처리: video_id와 단어/숙어 기준으로 중복 제거 및 병합
      - 같은 단어/숙어의 경우: 뜻과 예문을 합침 (중복 제거)
      - 다른 뜻이나 예문이 있으면 추가
      - 빈도수는 고려하지 않음
    - 출력: {video_id: 비디오 아이디, words: [{단어: [뜻1, 뜻2, ...], 품사: 품사, 동의어: [동의어1, 동의어2], 예문: 예문}, ...], phrases: [{숙어: [뜻1, 뜻2], 예문: 예문}, ...]}
- ◻️ LLM 서비스 통합 모듈 구현
  - 전체 워크플로우 통합 함수 (`app/services/llm/processor.py`)
    - 입력: TranscriptResponse (video_id, transcript: List[TranscriptChunk])
    - 처리:
      1. 청크 텍스트 추출
      2. 1단계: 단어 및 숙어 추출 (병렬)
      3. 2단계: 단어 및 숙어 상세 정보 생성 (병렬)
      4. 3단계: 결과 병합
    - 출력: 병합된 최종 결과 (words, phrases 분리)
  - 에러 핸들링 및 재시도 로직
  - 타임아웃 처리
  - 부분 실패 처리 (일부 청크 실패 시에도 나머지 처리 계속)
- ◻️ 단어장 응답 스키마 정의
  - 단어장 응답 스키마 정의 (`app/models/schemas.py`)
    - WordEntry: 단어 정보 (단어, 뜻 리스트, 품사, 동의어, 예문)
    - PhraseEntry: 숙어 정보 (숙어, 뜻 리스트, 예문)
    - VocabularyResponse: 최종 단어장 응답 (video_id, words: List[WordEntry], phrases: List[PhraseEntry])
- ◻️ API 엔드포인트 구현
  - 단어장 생성 엔드포인트 추가 (`app/routes/video.py`)
    - `POST /api/video/{video_id}/vocabulary` 엔드포인트 구현
    - TranscriptResponse를 받아서 LLM 처리 후 VocabularyResponse 반환
    - 에러 핸들링 및 예외 처리
- ◻️ 모듈 단위 테스트 및 예외 처리
  - LLM API 호출 실패 시 예외 처리
  - JSON 파싱 실패 처리
  - 타임아웃 처리
  - 네트워크 오류 처리
  - 테스트용 Mock 구현 (vLLM 서버 응답 시뮬레이션)
  - 각 단계별 단위 테스트 작성
  - 엔드포인트 통합 테스트 작성

## ◻️ Phase 5: 단어장 생성 및 응답
- ◻️ 단어장 스키마 정의
- ◻️ 단어장 생성/포맷팅 로직 구현
- ◻️ 최종 응답용 엔드포인트 통합
- ◻️ 기능별 수동/자동 테스트 작성

## ◻️ Phase 6: 통합 및 엔드투엔드 테스트
- ◻️ Phase 3~5 기능 통합 및 시나리오 테스트
- ◻️ 엔드투엔드 테스트 케이스 설계 및 실행
- ◻️ 배포 준비 사항 점검 및 문서화

# 4. 현재 진행 상태

- 완료: Phase 1, Phase 2, 로깅 미들웨어 추가 작업, Phase 3 (자막 추출 서비스)
- 진행 중: Phase 4 (LLM 처리 서버 구축)
- 예정: Phase 5 (단어장 생성 및 응답), Phase 6 (통합 및 엔드투엔드 테스트)

# 5. 추후 과제

- **app/services/transcript.py**: 자막 청크 처리 과정을 요청 정보와 함께 세분화해 기록할 수 있는 전용 로거 도입 검토 (별도 로거/핸들러 및 요청 컨텍스트 연계)
