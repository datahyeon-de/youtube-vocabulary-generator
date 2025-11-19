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
- ◻️ LLM 연동 방식 확정 (외부 API 또는 자체 서버)
  - OpenAI API, Anthropic Claude API, 자체 서버(Ollama 등) 중 선택
  - API 키 및 설정 관리 방법 결정
  - 비용 및 성능 고려사항 검토
- ◻️ LLM 의존성 추가 및 설정 모듈 구성
  - 선택한 LLM 라이브러리 의존성 추가 (`requirements.txt`)
  - LLM 설정 모듈 생성 (`app/core/llm_config.py` 또는 `app/services/llm/`)
  - 환경 변수 관리 (API 키, 모델명 등)
- ◻️ 자막 청크 기반 핵심 단어 추출 로직 구현
  - LLM 프롬프트 설계 (단어 추출용)
  - 청크별 단어 추출 함수 구현 (`app/services/llm/extract_words.py`)
  - 중복 단어 제거 및 빈도수 집계 로직
  - 단어 난이도 분류 로직 (선택사항)
- ◻️ 한국어 의미 생성 로직 구현
  - LLM 프롬프트 설계 (한국어 뜻 생성용)
  - 단어별 한국어 뜻 생성 함수 구현 (`app/services/llm/generate_meanings.py`)
  - 컨텍스트 기반 의미 생성 (문맥 고려)
- ◻️ 도메인 분류 로직 정립
  - LLM 프롬프트 설계 (도메인 분류용)
  - 도메인 분류 함수 구현 (`app/services/llm/classify_domain.py`)
  - 도메인 카테고리 정의 (예: 기술, 과학, 역사, 음악 등)
- ◻️ LLM 서비스 통합 모듈 구현
  - 전체 워크플로우 통합 함수 (`app/services/llm/processor.py`)
  - 청크별 처리 및 결과 병합 로직
  - 에러 핸들링 및 재시도 로직
- ◻️ 모듈 단위 테스트 및 예외 처리
  - LLM API 호출 실패 시 예외 처리
  - 타임아웃 처리
  - Rate limiting 처리 (API 호출 제한)
  - 테스트용 Mock 구현

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
