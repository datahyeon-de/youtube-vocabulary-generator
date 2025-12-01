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

## ✅ Phase 4: LLM 처리 서버 구축
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
  - 단어 추출 프롬프트 템플릿 (1단계, 한국어) - v10 버전 사용
  - 숙어 추출 프롬프트 템플릿 (1단계, 한국어) - v1 버전 사용
  - 단어 상세 정보 프롬프트 템플릿 (2단계: 동의어, 예문, 한국어) - v1, v7 버전 지원, 재시도 로직 포함
  - 숙어 예문 생성 프롬프트 템플릿 (2단계: 예문, 한국어) - v1, v7 버전 지원, 재시도 로직 포함
  - JSON 응답 형식 명시 (각 프롬프트에 포함)
  - 프롬프트 A/B 테스트 수행 및 최적 버전 선택 완료
- ✅ 1단계: 단어 및 숙어 추출 로직 구현
  - ✅ 단어 추출 함수 구현 (`app/services/llm/extract_words.py`)
    - 입력: 청크 텍스트 리스트, video_id
    - 프롬프트: 단어 추출용 (모든 단어 추출, 문맥상 사용되는 뜻 최대 2개, 품사 포함)
    - 출력: {videoId: video_id, result: {단어: {품사: "n", 뜻: [뜻1, 뜻2]}, ...}}
    - 구현 완료: 청크별 병렬 처리 (asyncio.gather), 결과 병합, 에러 핸들링, 로깅, 부분 실패 허용
    - 내부 헬퍼 함수 `_extract_words_from_single_chunk` 구현
  - ✅ 숙어 추출 함수 구현 (`app/services/llm/extract_phrases.py`)
    - 입력: 청크 텍스트 리스트, video_id
    - 프롬프트: 숙어 추출용 (idiom, phrasal verb, collocation 기준, 두 단어 이상 강제)
    - 출력: {videoId: video_id, result: {숙어: 뜻, ...}}
    - 구현 완료: 청크별 병렬 처리 (asyncio.gather), 결과 병합, 에러 핸들링, 로깅, 부분 실패 허용
    - 내부 헬퍼 함수 `_extract_phrases_from_single_chunk` 구현
    - 프롬프트 규칙 강화: 단일 단어 제외, 관용적 의미만 추출
  - ◻️ 병렬 처리 로직 (청크별로 단어/숙어 추출 프롬프트 동시 전송) - MVP에서는 스킵
- ✅ 2단계: 단어 및 숙어 상세 정보 생성 로직 구현
  - ✅ 단어 상세 정보 생성 함수 구현 (`app/services/llm/enrich_words.py`)
    - 입력: 1단계 단어 추출 결과 ({단어: {품사: "n", 뜻: [뜻1, 뜻2]}, ...})
    - 프롬프트: 동의어, 예문 생성용 (품사는 1단계에서 이미 추출됨, 원문 청크 불필요)
    - 출력: {videoId: video_id, result: {단어: {동의어: [동의어1, 동의어2], 예문: 예문}, ...}}
    - 구현 완료: 1단계 결과를 한 번에 처리 (청크별 분리 없음), 한 번의 LLM 호출
    - 재시도 로직 구현: v1 → v7 → v1 → v7 순서로 최대 4번 시도 (각 버전당 최대 2번)
  - ✅ 숙어 예문 생성 함수 구현 (`app/services/llm/enrich_phrases.py`)
    - 입력: 1단계 숙어 추출 결과 ({숙어: 뜻, ...})
    - 프롬프트: 예문 생성용 (원문 청크 불필요)
    - 출력: {videoId: video_id, result: {숙어: {예문: 예문}, ...}}
    - 구현 완료: 1단계 결과를 한 번에 처리 (청크별 분리 없음), 한 번의 LLM 호출
    - 재시도 로직 구현: v1 → v7 → v1 → v7 순서로 최대 4번 시도 (각 버전당 최대 2번)
- ✅ 3단계: 결과 병합 및 통합 로직 구현
  - ✅ 결과 병합 함수 구현 (`app/services/llm/merge_results.py`)
    - 입력: 1단계 및 2단계 결과 (word_extraction_result, phrase_extraction_result, word_enrichment_result, phrase_enrichment_result)
    - 처리: video_id와 단어/숙어 기준으로 중복 제거 및 병합
      - 같은 단어/숙어의 경우: 뜻과 예문을 합침 (중복 제거)
      - 다른 뜻이나 예문이 있으면 추가
      - 빈도수는 고려하지 않음
    - 출력: {videoId: video_id, words: [{word: 단어, pos: 품사, meanings: [뜻1, 뜻2], synonyms: [동의어1, 동의어2], example: 예문}, ...], phrases: [{phrase: 숙어, meaning: 뜻, example: 예문}, ...]}
    - 구현 완료: 단어/숙어 병합 로직, 1단계/2단계 결과 통합, 로깅
- ✅ LLM 서비스 통합 모듈 구현
  - ✅ 전체 워크플로우 통합 함수 (`app/services/llm/processor.py`)
    - 입력: 청크 텍스트 리스트 (List[str]), video_id
    - 처리:
      1. 입력 검증 (청크 텍스트, video_id)
      2. 1단계: 단어 및 숙어 추출 (병렬 처리, asyncio.gather)
      3. 2단계: 단어 및 숙어 상세 정보 생성 (병렬 처리, asyncio.gather, 재시도 로직 포함)
      4. 3단계: 결과 병합 (merge_results 호출)
    - 출력: 병합된 최종 결과 (words, phrases 분리된 딕셔너리)
    - 구현 완료: 전체 워크플로우 통합, 에러 핸들링, 부분 실패 처리, 로깅
- ✅ 단어장 응답 스키마 정의
  - ✅ 단어장 응답 스키마 정의 (`app/models/schemas.py`)
    - WordEntry: 단어 정보 (word, pos, meanings: List[str], synonyms: List[str], example)
    - PhraseEntry: 숙어 정보 (phrase, meaning, example)
    - VocabularyResponse: 최종 단어장 응답 (video_id, words: List[WordEntry], phrases: List[PhraseEntry], status, message)
    - 구현 완료: Pydantic 모델 정의, JSON 스키마 예시 포함
- ✅ API 엔드포인트 구현
  - ✅ 단어장 생성 엔드포인트 추가 (`app/routes/video.py`)
    - `POST /api/video/{video_id}/vocabulary` 엔드포인트 구현
    - 자막 추출 → 청크 텍스트 추출 → LLM 처리 → Pydantic 모델 변환 → VocabularyResponse 반환
    - 에러 핸들링 및 예외 처리 (사용자 친화적 메시지, 상세 로깅)
    - 구현 완료: 전체 워크플로우 통합, 에러 처리, 로깅
- ✅ 모듈 단위 테스트 및 예외 처리
  - LLM API 호출 실패 시 예외 처리
  - JSON 파싱 실패 처리
  - 타임아웃 처리
  - 네트워크 오류 처리
  - 각 단계별 단위 테스트 작성 (`tests/test_services/test_llm_extract_words.py`, `test_llm_extract_phrases.py`, `test_llm_enrich_words.py`, `test_llm_enrich_phrases.py`)
  - 프롬프트 A/B 테스트 모듈 구현 (`tests/test_services/test_llm_prompt_ab_test.py`)
    - 1단계 프롬프트 A/B 테스트 (단어 추출, 숙어 추출)
    - 2단계 프롬프트 A/B 테스트 (단어 상세 정보 생성, 숙어 예문 생성)
    - vLLM 서버 상태 확인 로직 포함
    - 테스트 결과 JSON 파일 생성
  - ✅ 엔드포인트 통합 테스트 작성
    - `POST /api/video/{video_id}/vocabulary` 엔드포인트 테스트 (`tests/test_routes/test_video.py`)
      - 정상 케이스 테스트 (`test_post_generate_vocabulary_success`)
        - vLLM 서버 실행 여부 확인 (skip_if_server_unavailable fixture)
        - 응답 구조 검증 (words, phrases 리스트 및 각 엔트리 구조)
        - 긴 타임아웃 설정 (5분, LLM 처리 시간 고려)
      - 에러 케이스 테스트 (`test_post_generate_vocabulary_invalid_video_id`)
        - 존재하지 않는 Video ID로 400 에러 확인
    - 서버 실행 여부 확인 fixture 추가 (`tests/test_routes/conftest.py`)
      - `server_available`: FastAPI 서버 실행 여부 확인
      - `skip_if_server_unavailable`: 서버가 없으면 테스트 자동 스킵


# 4. 현재 진행 상태

- ✅ **MVP 완료**: Phase 1, Phase 2, 로깅 미들웨어 추가 작업, Phase 3 (자막 추출 서비스), Phase 4 (LLM 처리 서버 구축)
  - Phase 4 세부 완료 항목:
    - vLLM 서버 연동 설정
    - LLM 클라이언트 모듈 구현
    - 프롬프트 템플릿 모듈 구현 (A/B 테스트 완료)
    - 1단계: 단어 및 숙어 추출 로직 구현
    - 2단계: 단어 및 숙어 상세 정보 생성 로직 구현 (재시도 로직 포함)
    - 3단계: 결과 병합 및 통합 로직 구현
    - LLM 서비스 통합 모듈 구현
    - 단어장 응답 스키마 정의 (WordEntry, PhraseEntry, VocabularyResponse)
    - API 엔드포인트 구현 (`POST /api/video/{video_id}/vocabulary`)
    - 엔드포인트 통합 테스트 작성
- 🎯 **다음 단계**: 고도화 및 세부 개선 작업 (아래 "추후 과제" 섹션 참조)

# 5. 고도화 및 개선 과제

## 5.1 에러 처리 및 안정성 개선

- **app/services/llm/extract_words.py, extract_phrases.py**: 1단계 단어/숙어 추출 과정에서 실패한 청크에 대한 재시도 로직 구현
  - 현재 상태: 부분 실패 허용하지만 실패한 청크는 재시도하지 않음
  - 개선 방향: 실패한 청크를 별도로 수집하여 최대 N번 재시도 (N은 설정 가능)
  - 고려사항: 무한 재시도 방지, 재시도 간격 설정, 재시도 횟수 로깅

- **app/services/llm/processor.py**: 전체 워크플로우 에러 처리 강화
  - 현재 상태: 부분 실패 허용, 빈 결과로 대체
  - 개선 방향: 
    - 단계별 실패율 모니터링 및 임계값 설정
    - 실패 원인별 세분화된 에러 메시지
    - 실패한 단계에 대한 상세 로깅 및 리포트 생성

- **app/routes/video.py**: 에러 응답 개선
  - 현재 상태: 사용자 친화적 메시지 제공, 상세 로깅
  - 개선 방향:
    - 에러 타입별 세분화된 HTTP 상태 코드
    - 에러 발생 시점 추적을 위한 request_id 추가
    - 에러 발생 빈도 모니터링

## 5.2 성능 최적화

- **병렬 처리 최적화**: 
  - 현재 상태: 청크별 병렬 처리 (asyncio.gather)
  - 개선 방향:
    - 동시 요청 수 제한 (semaphore 사용)
    - 청크 크기별 동적 배치 처리
    - LLM 서버 부하 모니터링 및 백프레셔 처리

- **캐싱 전략 도입**:
  - 자막 추출 결과 캐싱 (동일 video_id에 대해)
  - LLM 처리 결과 캐싱 (선택적, 동일 입력에 대해)
  - 캐시 무효화 전략 수립

- **응답 시간 최적화**:
  - LLM 응답 스트리밍 고려 (긴 응답의 경우)
  - 청크 처리 우선순위 큐 도입
  - 타임아웃 설정 최적화

## 5.3 로깅 및 모니터링 개선

- **로그 출력 포맷 통일**:
  - 현재 상태: 각 모듈별로 로그 포맷이 상이함
  - 개선 방향:
    - 통일된 로그 포맷 정의 (JSON 또는 구조화된 텍스트)
    - 공통 필드 정의 (timestamp, level, module, video_id, request_id 등)
    - 로그 파싱 및 분석 용이성을 위한 구조화

- **app/services/transcript.py**: 자막 청크 처리 과정을 요청 정보와 함께 세분화해 기록할 수 있는 전용 로거 도입
  - 현재 상태: 기본 로깅 사용
  - 개선 방향:
    - 별도 로거/핸들러 및 요청 컨텍스트 연계
    - 청크별 처리 시간 측정
    - 토큰 수, 청크 수 등 메트릭 로깅

- **LLM 처리 메트릭 수집**:
  - 각 단계별 처리 시간 측정
  - LLM API 호출 성공/실패율 추적
  - 프롬프트 버전별 성능 비교
  - 토큰 사용량 추적

- **분산 추적 (Distributed Tracing)**:
  - 요청별 전체 워크플로우 추적
  - 각 단계별 소요 시간 분석
  - 병목 지점 식별

## 5.4 코드 품질 및 유지보수성

- **타입 힌팅 강화**:
  - 모든 함수에 완전한 타입 힌팅 추가
  - mypy를 통한 타입 체크 자동화

- **문서화 개선**:
  - API 문서 자동 생성 (OpenAPI/Swagger) 보완
  - 각 모듈별 상세 docstring 작성
  - 아키텍처 다이어그램 추가

- **테스트 커버리지 향상**:
  - 엣지 케이스 및 통합 테스트 시나리오 확장

## 5.5 기능 확장

- **프롬프트 버전 관리**:
  - 현재 상태: A/B 테스트 완료, 최적 버전 선택
  - 개선 방향:
    - 프롬프트 버전 동적 전환 기능
    - 프롬프트 버전별 A/B 테스트 지속 모니터링
    - 프롬프트 버전 롤백 기능


## 5.6 보안 및 인증

- **인증/인가 시스템 도입**:
  - API 키 기반 인증
  - JWT 토큰 기반 인증
  - 사용자별 요청 제한 (Rate Limiting)
  - 관련 문서: `docs/06_authentication-strategy.md`

- **입력 검증 강화**:
  - Video ID 형식 검증 강화
  - 악의적인 입력 방지
  - 요청 크기 제한

## 5.7 데이터베이스 연동

- **비디오 ID 기반 결과 캐싱**:
  - 현재 상태: 매 요청마다 LLM 처리 수행
  - 개선 방향:
    - `POST /api/video/{video_id}/vocabulary` 요청 시 DB에서 먼저 조회
    - 기존 결과가 있으면 DB에서 반환 (LLM 처리 생략)
    - 결과가 없거나 만료된 경우에만 LLM 처리 수행

- **처리 결과 저장**:
  - 현재 상태: 결과를 메모리에만 보관 (요청 종료 시 소실)
  - 개선 방향:
    - 새로운 비디오 ID로 조회된 경우 처리 결과를 DB에 저장
    - 저장 데이터: video_id, words, phrases, 생성 시간, 처리 시간 등
    - 결과 만료 정책 수립 (선택적 TTL)

- **요청 이력 관리**:
  - 사용자 요청 이력 저장 (선택적)
  - 통계 데이터 수집 (비디오별 처리 횟수, 인기 비디오 등)

## 5.8 기타 개선 사항

- **프롬프트 최적화**: A/B 테스트 결과 분석 문서 작성 완료 (`docs/04_prompt-ab-test-analysis.md`)
  - 지속적인 프롬프트 개선 및 모니터링

- **환경 설정 관리**:
  - 환경별 설정 파일 분리 (dev, staging, prod)
  - 민감 정보 관리 (환경 변수, secrets 관리)

- **배포 자동화**:
  - CI/CD 파이프라인 구축
  - 자동 테스트 실행
  - 자동 배포 스크립트
