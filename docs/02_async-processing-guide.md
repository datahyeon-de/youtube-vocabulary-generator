# FastAPI 비동기 처리 및 LLM 통합 가이드

FastAPI 프로젝트에서 비동기 처리, LLM 통합, 사용자 경험 최적화에 대한 스터디 문서입니다.

---

## 📋 목차

1. [비동기 처리 기초](#1-비동기-처리-기초)
   - [왜 async를 사용하나요?](#11-왜-async를-사용하나요)
   - [httpx 사용법 기초](#12-httpx-사용법-기초)
   - [싱글톤 패턴 이해](#13-싱글톤-패턴-이해)
2. [비동기 vs 멀티프로세싱](#2-비동기-vs-멀티프로세싱)
   - [FastAPI에서의 선택 기준](#21-fastapi에서의-선택-기준)
   - [비동기와 멀티프로세싱 비교](#22-비동기와-멀티프로세싱-비교)
3. [LLM 통합 설계](#3-llm-통합-설계)
   - [Temperature 설정 기준](#31-temperature-설정-기준)
   - [vLLM 클라이언트 구조](#32-vllm-클라이언트-구조)
4. [전체 요청 흐름](#4-전체-요청-흐름)
   - [단계별 동기/비동기 판단](#41-단계별-동기비동기-판단)
   - [실제 구현 예시](#42-실제-구현-예시)
5. [사용자 경험 최적화](#5-사용자-경험-최적화)
   - [현재 구조의 한계](#51-현재-구조의-한계)
   - [개선 방법](#52-개선-방법)
6. [코드 구조 이해](#6-코드-구조-이해)
   - [VLLMClient 클래스 상세 설명](#61-vllmclient-클래스-상세-설명)
   - [비동기 함수 체인](#62-비동기-함수-체인)
7. [참고 자료](#7-참고-자료)

---

## 1. 비동기 처리 기초

### 1.1 왜 async를 사용하나요?

#### 동기 vs 비동기

**동기 방식 (일반적인 requests):**
```python
# 한 번에 하나씩만 처리
response1 = requests.get(url1)  # 1초 대기
response2 = requests.get(url2)  # 1초 대기
# 총 2초 소요
```

**비동기 방식 (httpx async):**
```python
# 여러 요청을 동시에 처리
response1, response2 = await asyncio.gather(
    client.get(url1),  # 동시에 시작
    client.get(url2)   # 동시에 시작
)
# 총 1초 소요 (병렬 처리)
```

**우리 프로젝트에서는 여러 청크를 동시에 처리해야 하므로 비동기가 적합합니다.**

---

### 1.2 httpx 사용법 기초

#### 기본 사용법

```python
import httpx

# 1. 클라이언트 생성
client = httpx.AsyncClient(
    base_url="http://tc-server-gpu:8000",  # 기본 URL
    timeout=60  # 타임아웃 설정
)

# 2. POST 요청 보내기
response = await client.post(
    "/v1/chat/completions",  # 엔드포인트 (base_url 뒤에 붙음)
    json={  # JSON 데이터 전송
        "model": "Qwen/Qwen2.5-14B-Instruct-AWQ",
        "messages": [{"role": "user", "content": "안녕하세요"}]
    }
)

# 3. 응답 확인
result = response.json()  # JSON으로 파싱
print(result)

# 4. 연결 종료
await client.aclose()
```

#### httpx.AsyncClient 주요 특징

- **비동기 HTTP 클라이언트**: 여러 요청을 동시에 처리 가능
- **연결 풀 관리**: 내부적으로 연결을 재사용하여 효율적
- **타임아웃 설정**: 요청별 또는 클라이언트별 타임아웃 설정 가능

---

### 1.3 싱글톤 패턴 이해

#### 개념 설명

싱글톤은 프로그램 전체에서 하나의 인스턴스만 존재하도록 보장하는 디자인 패턴입니다.

#### 예시로 이해하기

**싱글톤 없이 (매번 새로 만들기):**
```python
# 함수 호출할 때마다 새 클라이언트 생성
def process_chunk1():
    client = VLLMClient()  # 클라이언트 1 생성
    client.chat_completion(...)

def process_chunk2():
    client = VLLMClient()  # 클라이언트 2 생성 (또 새로 만듦!)
    client.chat_completion(...)

# 문제점: 클라이언트를 여러 개 만들면 연결이 많아져서 비효율적
```

**싱글톤 사용 (하나만 만들고 재사용):**
```python
# 전역 변수로 하나만 저장
_vllm_client = None

def get_vllm_client():
    global _vllm_client
    if _vllm_client is None:  # 없으면 만들기
        _vllm_client = VLLMClient()
    return _vllm_client  # 있으면 기존 것 반환

# 사용
def process_chunk1():
    client = get_vllm_client()  # 첫 번째 호출: 새로 생성
    client.chat_completion(...)

def process_chunk2():
    client = get_vllm_client()  # 두 번째 호출: 기존 것 재사용!
    client.chat_completion(...)

# 장점: 클라이언트를 하나만 만들어서 효율적
```

#### 왜 싱글톤을 사용하나요?

1. **리소스 절약**: HTTP 연결을 하나만 유지
2. **설정 일관성**: 같은 설정으로 통일
3. **연결 풀 관리**: httpx가 내부적으로 연결 풀을 관리

---

**[↑ 목차로 돌아가기](#📋-목차)**

---

## 2. 비동기 vs 멀티프로세싱

### 2.1 FastAPI에서의 선택 기준

#### 멀티프로세싱이란?

여러 프로세스를 동시에 실행하는 방식입니다.

```python
from multiprocessing import Process

def process_chunk(chunk):
    # 각 프로세스가 독립적으로 실행
    client = VLLMClient()
    result = client.chat_completion(...)
    return result

# 여러 프로세스로 실행
processes = []
for chunk in chunks:
    p = Process(target=process_chunk, args=(chunk,))
    p.start()
    processes.append(p)
```

---

### 2.2 비동기와 멀티프로세싱 비교

| 항목 | 비동기 (async/await) | 멀티프로세싱 |
|------|---------------------|-------------|
| **동작 방식** | 하나의 프로세스에서 여러 작업을 번갈아가며 처리 | 여러 프로세스를 동시에 실행 |
| **메모리 사용** | 적음 (하나의 프로세스) | 많음 (프로세스마다 메모리 복사) |
| **속도** | I/O 대기 시간 동안 다른 작업 처리 | CPU 집약적 작업에 유리 |
| **적합한 작업** | 네트워크 요청, 파일 I/O | CPU 계산이 많은 작업 |
| **FastAPI와의 호환성** | ✅ 완벽 지원 (기본이 비동기) | ⚠️ 복잡함 (별도 설정 필요) |

#### 우리 프로젝트에서는?

우리 작업은 **네트워크 요청(I/O 작업)**이므로 **비동기가 적합**합니다.

```python
# 비동기: 네트워크 대기 시간 동안 다른 요청 처리
async def process_chunks():
    tasks = [
        client.chat_completion(chunk1),  # 요청 1 보냄 (대기 중...)
        client.chat_completion(chunk2),  # 요청 2 보냄 (대기 중...)
        client.chat_completion(chunk3),  # 요청 3 보냄 (대기 중...)
    ]
    # 세 요청이 동시에 진행됨!
    results = await asyncio.gather(*tasks)
    # 총 시간: 가장 느린 요청 시간 (예: 2초)
```

```python
# 멀티프로세싱: 각 프로세스가 독립적으로 실행
# 문제점:
# 1. FastAPI는 기본이 비동기인데 멀티프로세싱은 복잡함
# 2. 메모리를 많이 사용 (프로세스마다 메모리 복사)
# 3. 네트워크 요청에는 오히려 비효율적
```

#### FastAPI에서 비동기를 사용하는 이유

FastAPI는 비동기 프레임워크입니다:

```python
# FastAPI 엔드포인트
@router.post("/api/video/{video_id}/vocabulary")
async def create_vocabulary(video_id: str):  # async 함수
    # 비동기 함수를 호출하면 자연스럽게 병렬 처리
    result = await process_vocabulary(video_id)
    return result
```

**비동기를 사용하면:**
- FastAPI와 자연스럽게 통합
- 여러 요청을 동시에 처리 가능
- 메모리 효율적

---

**[↑ 목차로 돌아가기](#📋-목차)**

---

## 3. LLM 통합 설계

### 3.1 Temperature 설정 기준

#### Temperature란?

LLM의 출력 다양성을 조절하는 파라미터입니다.

- **낮은 값 (0.0 ~ 0.3)**: 일관적이고 예측 가능한 출력
- **중간 값 (0.5 ~ 0.7)**: 균형 잡힌 출력
- **높은 값 (0.8 ~ 2.0)**: 창의적이고 다양한 출력

#### 우리 프로젝트에서의 설정

```python
# 1단계: 단어/숙어 추출
temperature=0.3  # 낮게 설정 (일관된 결과 필요)

# 2단계: 상세 정보 생성
temperature=0.7  # 중간 값 (적당한 다양성)
```

#### 왜 이렇게 설정하나요?

1. **단어 추출 (temperature=0.3)**:
   - 같은 입력에 대해 같은 단어가 추출되어야 함
   - 너무 높으면 매번 다른 결과가 나올 수 있음

2. **상세 정보 생성 (temperature=0.7)**:
   - 예문 생성 시 적당한 다양성 유지
   - 너무 낮으면 예문이 단조로울 수 있음

#### Temperature 값별 예시

```python
# temperature=0.1 (매우 낮음)
입력: "Hello"
출력: "안녕하세요" (항상 같은 결과)

# temperature=0.7 (중간)
입력: "Hello"
출력: 
- "안녕하세요"
- "안녕"
- "여보세요"
(약간의 다양성)

# temperature=1.5 (높음)
입력: "Hello"
출력:
- "안녕하세요"
- "반갑습니다"
- "좋은 아침입니다"
- "인사드립니다"
(매우 다양한 결과)
```

#### 우리 프로젝트 권장 설정

```python
# 단어/숙어 추출: 정확성 중시
temperature=0.3  # 일관된 결과

# 상세 정보 생성: 적당한 다양성
temperature=0.7  # 예문이 자연스럽게

# 필요시 조정 가능
temperature=0.5  # 더 보수적
temperature=0.9  # 더 창의적
```

---

### 3.2 vLLM 클라이언트 구조

#### 전체 구조

```python
# ============================================
# 1단계: 필요한 라이브러리 가져오기
# ============================================
import json          # JSON 파싱용
import asyncio       # 비동기 처리용
from typing import Dict, List, Optional, Any  # 타입 힌팅
import httpx         # HTTP 클라이언트
from app.core.config import settings  # 설정 가져오기
from app.core.logging import get_access_logger, get_error_logger  # 로깅
```

#### VLLMClient 클래스 - 초기화 부분

```python
class VLLMClient:
    """vLLM 서버와 통신하는 클라이언트"""
    
    def __init__(self):
        # config.py에서 설정값 가져오기
        self.base_url = settings.VLLM_SERVER_URL  # "http://tc-server-gpu:8000"
        self.api_endpoint = settings.VLLM_SERVER_ENDPOINT  # "/v1/chat/completions"
        self.model = settings.VLLM_SERVER_MODEL  # "Qwen/Qwen2.5-14B-Instruct-AWQ"
        self.timeout = settings.VLLM_SERVER_TIMEOUT  # 60초
        self.max_retries = settings.VLLM_SERVER_MAX_RETRIES  # 3회
        self.retry_delay = settings.VLLM_RETRY_DELAY  # 3초
        
        # httpx 비동기 클라이언트 생성
        # 이 클라이언트는 여러 요청을 동시에 보낼 수 있음
        self.client = httpx.AsyncClient(
            base_url=self.base_url,  # 기본 URL 설정
            timeout=self.timeout     # 타임아웃 설정
        )
```

**설명:**
- `__init__`: 클라이언트 생성 시 설정값을 저장하고 httpx 클라이언트를 준비합니다.

---

**[↑ 목차로 돌아가기](#📋-목차)**

---

## 4. 전체 요청 흐름

### 4.1 단계별 동기/비동기 판단

#### 전체 흐름 시각화

```
사용자: "단어장 만들어줘" 버튼 클릭
  ↓
[FastAPI 라우터] async def create_vocabulary()
  ├─ 동기: Video ID 추출 (0.001초)
  ├─ 동기: 자막 추출 (2초) - YouTube API
  ├─ 동기: 청크 생성 (0.1초)
  ├─ ⭐ 비동기: LLM 처리 시작
  │   ├─ 청크1: 단어 추출 (2초) ┐
  │   ├─ 청크1: 숙어 추출 (2초) │
  │   ├─ 청크2: 단어 추출 (2초) ├─ 모두 동시에 실행!
  │   ├─ 청크2: 숙어 추출 (2초) │
  │   └─ ... (총 20개 요청)    ┘
  │   → 총 시간: 2초 (병렬 처리)
  ├─ 동기: 결과 병합 (0.1초)
  └─ 동기: 응답 반환 (0.001초)
  ↓
사용자에게 결과 전달 (총 대기 시간: 약 4.2초)
```

#### 동기 함수를 사용하는 경우

1. **CPU 작업 (계산, 파싱)**
   ```python
   def count_tokens(text: str) -> int:  # 동기
       return len(tokenizer.encode(text))
   ```

2. **매우 빠른 작업 (1ms 이하)**
   ```python
   def extract_video_id(url: str) -> str:  # 동기
       return url.split("v=")[1]
   ```

3. **동기 라이브러리만 지원**
   ```python
   def get_transcript(video_id: str):  # 동기
       # youtube-transcript-api가 동기만 지원
       return api.fetch(video_id)
   ```

#### 비동기 함수를 사용하는 경우

1. **네트워크 I/O (HTTP 요청)**
   ```python
   async def call_llm(prompt: str):  # 비동기
       response = await client.post(url, json=data)
       return response
   ```

2. **여러 작업을 병렬 처리해야 할 때**
   ```python
   async def process_chunks(chunks: List[str]):  # 비동기
       tasks = [process_chunk(c) for c in chunks]
       return await asyncio.gather(*tasks)  # 병렬 처리
   ```

3. **데이터베이스 작업 (대부분 비동기 지원)**
   ```python
   async def get_user(user_id: int):  # 비동기
       return await db.fetch_one(query)
   ```

---

### 4.2 실제 구현 예시

#### 단어장 생성 API

```python
# app/routes/video.py
@router.post("/{video_id}/vocabulary", response_model=VocabularyResponse)
async def create_vocabulary(video_id: str):  # ⭐ 비동기
    """
    단어장 생성 API
    
    전체 흐름:
    1. 자막 추출 (동기)
    2. LLM 처리 (비동기 - 병렬)
    3. 결과 병합 (동기)
    4. 응답 반환
    """
    try:
        # 1단계: 자막 추출 (동기 - YouTube API)
        transcript_response = TranscriptResponse(
            video_id=video_id,
            transcript=get_transcript(video_id),  # 동기 함수
            status="success"
        )
        
        # 2단계: LLM 처리 (비동기 - 병렬 처리)
        vocabulary_data = await process_vocabulary(transcript_response)  # ⭐ await
        
        # 3단계: 결과 병합 (동기)
        merged = merge_results(vocabulary_data)  # 동기 함수
        
        # 4단계: 응답 반환
        return VocabularyResponse(
            video_id=video_id,
            words=merged["words"],
            phrases=merged["phrases"]
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

#### 사용자 입장에서의 대기 시간

**시나리오: 10개 청크 처리**

```
사용자: 버튼 클릭
  ↓
[대기 시작...]
  ├─ Video ID 추출: 0.001초
  ├─ 자막 추출: 2초
  ├─ 청크 생성: 0.1초
  ├─ LLM 처리: 2초 (10개 청크 × 2개 요청 = 20개 요청을 병렬 처리)
  ├─ 결과 병합: 0.1초
  └─ 응답 반환: 0.001초
  ↓
[대기 종료] 총 4.2초 후 결과 수신
```

**만약 비동기를 사용하지 않았다면:**
```
LLM 처리: 20개 요청 × 2초 = 40초
총 대기 시간: 42초 (10배 느림!)
```

---

**[↑ 목차로 돌아가기](#📋-목차)**

---

## 5. 사용자 경험 최적화

### 5.1 현재 구조의 한계

#### FastAPI의 async def와 사용자 경험

**핵심 정리:**
- FastAPI의 `async def`는 **서버 측 효율성**을 위한 것입니다.
- **클라이언트(사용자) 입장에서는 여전히 요청을 보내고 응답을 기다려야 합니다.**

#### 현재 구조 (일반 API)

```python
# 백엔드
@router.post("/{video_id}/vocabulary")
async def create_vocabulary(video_id: str):
    # 4초 동안 처리
    result = await process_vocabulary(...)
    return result  # 4초 후 응답
```

```javascript
// 프론트엔드
async function createVocabulary(videoId) {
    // ⏳ 여기서 4초 동안 대기 (브라우저가 멈춤)
    const response = await fetch(`/api/video/${videoId}/vocabulary`, {
        method: 'POST'
    });
    // 4초 후에야 다음 코드 실행
    const result = await response.json();
    showVocabulary(result);
}
```

**사용자 경험:**
- 버튼 클릭 → 4초 대기 → 결과 표시
- 이 동안 다른 작업 불가

---

### 5.2 개선 방법

#### 방법 1: 백그라운드 작업 + 폴링

**백엔드 변경:**

```python
# app/routes/video.py
from fastapi import BackgroundTasks
import uuid

# 작업 상태 저장 (실제로는 Redis나 DB 사용)
job_storage = {}

@router.post("/{video_id}/vocabulary/start")
async def start_vocabulary_creation(
    video_id: str,
    background_tasks: BackgroundTasks
):
    """작업 시작 (즉시 응답)"""
    job_id = str(uuid.uuid4())
    
    # 백그라운드에서 작업 시작
    background_tasks.add_task(
        create_vocabulary_background, 
        job_id, 
        video_id
    )
    
    # 즉시 응답 (작업 ID만 반환)
    return {
        "job_id": job_id,
        "status": "started",
        "message": "단어장 생성이 시작되었습니다"
    }

@router.get("/vocabulary/status/{job_id}")
async def get_vocabulary_status(job_id: str):
    """작업 상태 확인"""
    job = job_storage.get(job_id)
    if not job:
        return {"status": "not_found"}
    return job
```

**프론트엔드 변경:**

```javascript
// 1. 작업 시작 (즉시 응답)
async function startVocabularyCreation(videoId) {
    const response = await fetch(`/api/video/${videoId}/vocabulary/start`, {
        method: 'POST'
    });
    const { job_id } = await response.json();
    
    // ✅ 즉시 응답 받음! 사용자는 다른 작업 가능
    showMessage("단어장 생성이 시작되었습니다.");
    
    // 2. 주기적으로 상태 확인 (폴링)
    checkJobStatus(job_id);
}

// 3. 상태 확인 함수 (폴링)
function checkJobStatus(jobId) {
    const interval = setInterval(async () => {
        const response = await fetch(`/api/video/vocabulary/status/${jobId}`);
        const status = await response.json();
        
        // 진행률 표시
        updateProgressBar(status.progress);
        
        if (status.status === 'completed') {
            clearInterval(interval);
            // 결과 표시
            showVocabulary(status.data);
        } else if (status.status === 'failed') {
            clearInterval(interval);
            showError(status.error);
        }
    }, 1000); // 1초마다 확인
}
```

**사용자 경험:**
1. 버튼 클릭 → 즉시 "작업 시작됨" 메시지
2. 사용자는 다른 페이지 이동, 다른 작업 가능
3. 백그라운드에서 작업 진행
4. 주기적으로 상태 확인 → 완료되면 알림

#### 방법 2: WebSocket으로 실시간 진행 상황 전송

```python
# app/routes/video.py
from fastapi import WebSocket

@router.websocket("/vocabulary/ws/{video_id}")
async def vocabulary_websocket(websocket: WebSocket, video_id: str):
    await websocket.accept()
    
    try:
        # 진행 상황 전송
        await websocket.send_json({"progress": 0, "message": "시작"})
        
        # 자막 추출
        transcript = get_transcript(video_id)
        await websocket.send_json({"progress": 25, "message": "자막 추출 완료"})
        
        # LLM 처리
        vocabulary = await process_vocabulary(transcript)
        await websocket.send_json({"progress": 75, "message": "LLM 처리 완료"})
        
        # 결과 병합
        result = merge_results(vocabulary)
        await websocket.send_json({
            "progress": 100,
            "message": "완료",
            "data": result
        })
        
    except Exception as e:
        await websocket.send_json({
            "progress": 0,
            "error": str(e)
        })
    finally:
        await websocket.close()
```

#### 비교표

| 방법 | 사용자 대기 | 다른 작업 가능 | 구현 복잡도 | 실시간 피드백 |
|------|------------|--------------|------------|--------------|
| **일반 API (현재)** | ⏳ 응답까지 대기 | ❌ 불가 | ✅ 간단 | ❌ 없음 |
| **백그라운드 + 폴링** | ✅ 즉시 응답 | ✅ 가능 | ⚠️ 중간 | ⚠️ 주기적 확인 |
| **WebSocket** | ✅ 즉시 연결 | ✅ 가능 | ⚠️ 중간 | ✅ 실시간 |
| **SSE** | ✅ 즉시 연결 | ✅ 가능 | ⚠️ 중간 | ✅ 실시간 |

---

**[↑ 목차로 돌아가기](#📋-목차)**

---

## 6. 코드 구조 이해

### 6.1 VLLMClient 클래스 상세 설명

#### chat_completion 메서드 - 핵심 로직

```python
async def chat_completion(
    self,
    messages: List[Dict[str, str]],  # 예: [{"role": "user", "content": "안녕"}]
    temperature: float = 0.7,        # 생성 온도 (0.0~2.0)
    max_tokens: Optional[int] = None # 최대 토큰 수
) -> Dict[str, Any]:
    """
    OpenAI 호환 chat completion API 호출
    """
    # 1단계: 요청 URL 만들기
    url = f"{self.base_url}{self.api_endpoint}"
    # 결과: "http://tc-server-gpu:8000/v1/chat/completions"
    
    # 2단계: 요청 데이터 준비
    payload = {
        "model": self.model,
        "messages": messages,
        "temperature": temperature,
    }
    
    if max_tokens:
        payload["max_tokens"] = max_tokens
    
    # 3단계: 재시도 로직 (최대 3번 시도)
    for attempt in range(self.max_retries):  # 0, 1, 2 (총 3번)
        try:
            # 4단계: HTTP POST 요청 보내기
            ACCESS_LOGGER.debug(f"vLLM API 요청 시도 {attempt + 1}/{self.max_retries}")
            
            response = await self.client.post(
                url,           # 요청 URL
                json=payload,  # JSON 데이터
                timeout=self.timeout  # 타임아웃
            )
            
            # 5단계: HTTP 상태 코드 확인 (200이 아니면 예외 발생)
            response.raise_for_status()
            
            # 6단계: 응답을 JSON으로 파싱
            result = response.json()
            ACCESS_LOGGER.debug(f"vLLM API 응답 수신 성공")
            return result  # 성공하면 결과 반환
            
        except httpx.HTTPError as e:
            # HTTP 오류 발생 시 (네트워크 오류, 500 에러 등)
            ERROR_LOGGER.error(f"vLLM API HTTP 오류 (시도 {attempt + 1}/{self.max_retries}): {str(e)}")
            
            # 마지막 시도가 아니면 잠시 기다렸다가 재시도
            if attempt < self.max_retries - 1:
                # exponential backoff: 3초, 6초, 9초...
                await asyncio.sleep(self.retry_delay * (attempt + 1))
            else:
                # 3번 모두 실패하면 예외 발생
                raise
                
        except json.JSONDecodeError as e:
            # JSON 파싱 실패 시
            ERROR_LOGGER.error(f"vLLM API JSON 파싱 오류: {str(e)}")
            raise ValueError(f"JSON 파싱 실패: {str(e)}")
            
        except Exception as e:
            # 예상치 못한 오류
            ERROR_LOGGER.error(f"vLLM API 예상치 못한 오류: {str(e)}")
            raise
```

**설명:**
- `async def`: 비동기 함수입니다.
- `await`: 비동기 작업이 끝날 때까지 대기합니다.
- **재시도**: 실패 시 최대 3번 재시도합니다.

#### extract_content_from_response 메서드

```python
async def extract_content_from_response(self, response: Dict[str, Any]) -> str:
    """
    API 응답에서 실제 생성된 텍스트 추출
    
    OpenAI API 응답 형식:
    {
        "choices": [
            {
                "message": {
                    "content": "실제 생성된 텍스트"
                }
            }
        ]
    }
    """
    try:
        # 1단계: choices 배열 가져오기
        choices = response.get("choices", [])
        if not choices:
            raise ValueError("응답에 choices가 없습니다")
        
        # 2단계: 첫 번째 choice의 message 가져오기
        message = choices[0].get("message", {})
        
        # 3단계: message에서 content(실제 텍스트) 가져오기
        content = message.get("content", "")
        
        if not content:
            raise ValueError("응답에 content가 없습니다")
        
        # 4단계: 앞뒤 공백 제거하고 반환
        return content.strip()
        
    except Exception as e:
        ERROR_LOGGER.error(f"응답에서 내용 추출 실패: {str(e)}")
        raise ValueError(f"응답 파싱 실패: {str(e)}")
```

**설명:**
- API 응답에서 실제 생성된 텍스트만 추출합니다.

---

### 6.2 비동기 함수 체인

#### 체인 구조

```
라우터 (async) 
  ↓ await
서비스 (async)
  ↓ await
클라이언트 (async)
  ↓ await
HTTP 요청 (비동기)
```

#### 실제 코드 흐름

```python
# app/routes/video.py
@router.post("/{video_id}/vocabulary")
async def create_vocabulary(video_id: str):  # 1. 라우터가 async
    # 2. 내부에서 비동기 함수 호출
    vocabulary = await process_vocabulary(transcript)  # await 필수
    return vocabulary

# app/services/llm/processor.py
async def process_vocabulary(...):  # 3. 이 함수도 async
    # 4. 더 깊은 곳에서 비동기 함수 호출
    results = await asyncio.gather(*tasks)  # await 사용
    return results

# app/services/llm/client.py
async def chat_completion(...):  # 5. 최종적으로 HTTP 요청도 async
    response = await client.post(...)  # await 사용
    return response
```

#### 핵심 원칙

**규칙: 비동기 함수를 호출하려면 호출하는 함수도 async여야 함**

```python
# ❌ 잘못된 예시 (동기 함수에서 비동기 함수 호출)
@router.post("/{video_id}/vocabulary")
def create_vocabulary(video_id: str):  # 동기 함수
    # 이렇게 하면 에러 발생!
    result = await process_vocabulary(...)  # SyntaxError!
    return result

# ✅ 올바른 예시
@router.post("/{video_id}/vocabulary")
async def create_vocabulary(video_id: str):  # 비동기 함수
    # await 사용 가능
    result = await process_vocabulary(...)  # 정상 작동
    return result
```

---

**[↑ 목차로 돌아가기](#📋-목차)**

---

## 7. 참고 자료

### 공식 문서

- **[FastAPI Documentation](https://fastapi.tiangolo.com/)**
  - FastAPI 공식 문서
  - 비동기 처리 가이드
  - Background Tasks 설명

- **[httpx Documentation](https://www.python-httpx.org/)**
  - httpx HTTP 클라이언트 문서
  - 비동기 HTTP 요청 처리
  - 타임아웃 및 재시도 설정

- **[Python asyncio Documentation](https://docs.python.org/3/library/asyncio.html)**
  - Python 비동기 프로그래밍 공식 문서
  - asyncio.gather 사용법
  - 비동기 함수 작성 가이드

### 추가 학습 자료

- **비동기 프로그래밍 패턴**: async/await 이해하기
- **싱글톤 패턴**: 디자인 패턴 이해하기
- **FastAPI Best Practices**: FastAPI 모범 사례

---

## 📌 요약

### 핵심 개념

1. **비동기(async)**: 여러 작업을 동시에 처리하여 속도 향상
2. **싱글톤**: 클라이언트를 하나만 만들어 재사용
3. **비동기 vs 멀티프로세싱**: 네트워크 요청에는 비동기가 적합
4. **Temperature**: 작업 목적에 맞게 조정 (추출=낮게, 생성=중간)

### 전체 흐름

1. **FastAPI 라우터**: 비동기 함수를 호출할 때는 `async def` 사용
2. **동기 함수**: CPU 작업, 빠른 작업, 동기 라이브러리 사용 시
3. **비동기 함수**: 네트워크 I/O, 병렬 처리 필요 시
4. **전체 흐름**: 대부분 동기, LLM 처리 부분만 비동기로 병렬 처리

### 사용자 경험

1. **현재 구조**: 사용자는 응답을 기다려야 함
2. **개선 방법**: 백그라운드 작업, WebSocket, SSE 등 별도 구현 필요
3. **프론트엔드**: 폴링 또는 WebSocket으로 상태 확인

---

**문서 버전**: 1.0  
**최종 업데이트**: 2025-11-20  
**작성 목적**: Phase 4 LLM 통합 개발 중 학습 내용 정리

---

> 💡 **팁**: 이 문서는 프로젝트 진행 중 학습한 내용을 정리한 것입니다. 새로운 질문이나 이해한 내용이 추가되면 계속 업데이트해주세요!

