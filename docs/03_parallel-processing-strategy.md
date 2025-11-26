# 단어/숙어 추출 병렬 처리 전략 분석

단어와 숙어 추출 로직의 병렬 처리 개선 방안에 대한 스터디 문서입니다.

---

## 📋 목차

1. [현재 구조 분석](#1-현재-구조-분석)
2. [병렬 처리 개선 방안](#2-병렬-처리-개선-방안)
3. [vLLM KV Cache OOM 위험 분석](#3-vllm-kv-cache-oom-위험-분석)
4. [전략 비교 및 권장사항](#4-전략-비교-및-권장사항)
5. [구현 방안](#5-구현-방안)

---

## 1. 현재 구조 분석

### 1.1 현재 구현 방식

**단어 추출 (`extract_words_from_chunks`):**
```python
# 모든 청크에 대해 병렬로 작업 생성
tasks = [
    _extract_words_from_single_chunk(chunk_text, idx, len(chunk_texts), video_id)
    for idx, chunk_text in enumerate(chunk_texts, start=1)
]

# 모든 작업을 병렬로 실행
results = await asyncio.gather(*tasks, return_exceptions=True)
```

**숙어 추출 (`extract_phrases_from_chunks`):**
```python
# 모든 청크에 대해 병렬로 작업 생성
tasks = [
    _extract_phrases_from_single_chunk(chunk_text, idx, len(chunk_texts), video_id)
    for idx, chunk_text in enumerate(chunk_texts, start=1)
]

# 모든 작업을 병렬로 실행
results = await asyncio.gather(*tasks, return_exceptions=True)
```

### 1.2 현재 실행 흐름

```
청크 1, 2, 3, ..., N
  ↓
[단어 추출] → 청크별 병렬 처리 → 결과 병합
  ↓ (완료 후)
[숙어 추출] → 청크별 병렬 처리 → 결과 병합
```

**특징:**
- 단어 추출과 숙어 추출이 **순차적으로** 실행됨
- 각 단계 내에서는 청크들이 **병렬로** 처리됨
- 총 LLM API 호출 횟수: `청크 개수 × 2` (단어 + 숙어)

**예시 (8개 청크):**
- 단어 추출: 8개 요청 동시 실행
- 숙어 추출: 8개 요청 동시 실행
- 총 16개 요청 (순차적)

---

## 2. 병렬 처리 개선 방안

### 2.1 방안 A: 완전 병렬 처리 (동시 실행)

**구조:**
```python
# 각 청크에 대해 단어/숙어 추출을 동시에 실행
tasks = [
    asyncio.gather(
        _extract_words_from_single_chunk(chunk_text, idx, len(chunk_texts), video_id),
        _extract_phrases_from_single_chunk(chunk_text, idx, len(chunk_texts), video_id)
    )
    for idx, chunk_text in enumerate(chunk_texts, start=1)
]

results = await asyncio.gather(*tasks, return_exceptions=True)
```

**실행 흐름:**
```
청크 1: [단어 추출] ─┐
      [숙어 추출] ─┘ → 동시 실행
청크 2: [단어 추출] ─┐
      [숙어 추출] ─┘ → 동시 실행
청크 3: [단어 추출] ─┐
      [숙어 추출] ─┘ → 동시 실행
...
청크 N: [단어 추출] ─┐
      [숙어 추출] ─┘ → 동시 실행
```

**특징:**
- 모든 청크의 단어/숙어 추출이 **동시에** 시작됨
- 총 LLM API 호출 횟수: `청크 개수 × 2` (동시 실행)
- **최대 동시 요청 수: `청크 개수 × 2`**

**예시 (8개 청크):**
- 동시 실행: 16개 요청 (8개 단어 + 8개 숙어)
- 총 소요 시간: 가장 오래 걸리는 요청 시간

### 2.2 방안 B: 순차적 처리 (현재 방식)

**구조:**
```python
# 1단계: 단어 추출
word_results = await extract_words_from_chunks(chunk_texts, video_id)

# 2단계: 숙어 추출
phrase_results = await extract_phrases_from_chunks(chunk_texts, video_id)
```

**실행 흐름:**
```
[단어 추출] → 8개 청크 병렬 처리 → 완료
  ↓
[숙어 추출] → 8개 청크 병렬 처리 → 완료
```

**특징:**
- 단어 추출 완료 후 숙어 추출 시작
- 각 단계 내에서는 청크들이 병렬 처리
- **최대 동시 요청 수: `청크 개수`**

**예시 (8개 청크):**
- 단어 추출: 8개 요청 동시 실행
- 숙어 추출: 8개 요청 동시 실행
- 총 소요 시간: 단어 추출 시간 + 숙어 추출 시간

### 2.3 방안 C: 조건부 병렬 처리 (하이브리드)

**구조:**
```python
# 설정에 따라 병렬/순차 선택
if settings.ENABLE_PARALLEL_WORD_PHRASE_EXTRACTION:
    # 방안 A: 완전 병렬
    tasks = [asyncio.gather(word_task, phrase_task) for ...]
else:
    # 방안 B: 순차적
    word_results = await extract_words_from_chunks(...)
    phrase_results = await extract_phrases_from_chunks(...)
```

**특징:**
- 환경 변수나 설정으로 제어 가능
- MVP에서는 순차적, 프로덕션에서는 병렬 처리 가능
- 자원 상황에 따라 유연하게 조정

---

## 3. vLLM KV Cache OOM 위험 분석

### 3.1 KV Cache란?

**Key-Value Cache (KV Cache):**
- Transformer 모델에서 이전 토큰의 Key와 Value를 캐싱하여 재계산을 방지
- 메모리 사용량이 **입력 토큰 수 × 모델 파라미터 수**에 비례
- 동시 요청이 많을수록 메모리 사용량이 급증

### 3.2 OOM 위험 요소

**1. 동시 요청 수**
- 방안 A (완전 병렬): 최대 `청크 개수 × 2` 개의 동시 요청
- 방안 B (순차적): 최대 `청크 개수` 개의 동시 요청
- **방안 A가 2배 더 많은 동시 요청 발생**

**2. 청크 크기**
- 현재 설정: 2000 토큰/청크
- 각 요청마다 KV Cache 메모리 할당
- 청크가 많을수록 메모리 사용량 증가

**3. 모델 크기**
- 현재 모델: Qwen/Qwen2.5-14B-Instruct-AWQ (14B 파라미터, AWQ 양자화)
- AWQ 양자화로 메모리 사용량 감소하지만, 여전히 상당한 메모리 필요

### 3.3 메모리 사용량 추정

**가정:**
- 청크 개수: 8개
- 토큰/청크: 2000 토큰
- 모델: 14B (AWQ 양자화)

**방안 A (완전 병렬):**
- 동시 요청: 16개 (8 단어 + 8 숙어)
- 예상 KV Cache 메모리: `16 × 2000 × 모델_파라미터_크기`
- **위험도: 높음** (OOM 가능성 높음)

**방안 B (순차적):**
- 동시 요청: 8개 (단어 또는 숙어)
- 예상 KV Cache 메모리: `8 × 2000 × 모델_파라미터_크기`
- **위험도: 중간** (OOM 가능성 낮음)

### 3.4 vLLM의 동시 처리 제한

**vLLM의 특징:**
- Continuous batching으로 동시 요청 처리
- GPU 메모리에 따라 최대 동시 요청 수 제한
- **일반적으로 8-16개 동시 요청이 안전한 범위**

**권장 동시 요청 수:**
- 소규모 GPU (24GB): 4-8개
- 중규모 GPU (40GB): 8-16개
- 대규모 GPU (80GB+): 16-32개

---

## 4. 전략 비교 및 권장사항

### 4.1 전략 비교표

| 항목 | 방안 A (완전 병렬) | 방안 B (순차적) | 방안 C (조건부) |
|------|-------------------|----------------|----------------|
| **처리 시간** | ⭐⭐⭐ 빠름 (동시 실행) | ⭐⭐ 보통 (순차 실행) | ⭐⭐⭐/⭐⭐ 설정에 따라 |
| **메모리 사용** | ⭐ 높음 (2배) | ⭐⭐ 낮음 (1배) | ⭐⭐/⭐ 설정에 따라 |
| **OOM 위험** | ⭐⭐⭐ 높음 | ⭐ 낮음 | ⭐⭐/⭐⭐⭐ 설정에 따라 |
| **구현 복잡도** | ⭐⭐ 중간 | ⭐ 쉬움 | ⭐⭐⭐ 복잡 |
| **유연성** | ⭐ 낮음 | ⭐ 낮음 | ⭐⭐⭐ 높음 |
| **MVP 적합성** | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |

### 4.2 MVP 단계 권장사항

**권장: 방안 B (순차적 처리)**

**이유:**
1. **안정성 우선**: OOM 위험 최소화
2. **구현 단순**: 현재 구조 유지, 추가 복잡도 없음
3. **충분한 성능**: 청크 내 병렬 처리로 이미 빠름
4. **디버깅 용이**: 단계별로 결과 확인 가능

**예상 성능:**
- 청크 8개 기준: 단어 추출 ~5초 + 숙어 추출 ~5초 = 총 ~10초
- 사용자 경험: 충분히 빠름 (비동기 처리로 블로킹 없음)

### 4.3 프로덕션 단계 권장사항

**권장: 방안 C (조건부 병렬 처리)**

**이유:**
1. **유연성**: 자원 상황에 따라 조정 가능
2. **확장성**: GPU 메모리 증가 시 병렬 처리 활성화
3. **모니터링**: 실제 사용량 기반으로 최적화 가능

**구현 전략:**
```python
# 설정 기반 분기
if settings.ENABLE_PARALLEL_WORD_PHRASE_EXTRACTION and chunk_count <= MAX_SAFE_CHUNKS:
    # 병렬 처리 (청크 수가 적을 때만)
    return await parallel_extraction(chunk_texts, video_id)
else:
    # 순차 처리 (안전한 기본값)
    return await sequential_extraction(chunk_texts, video_id)
```

---

## 5. 구현 방안

### 5.1 MVP: 순차적 처리 (방안 B)

**구현 위치:** `app/services/llm/processor.py` (신규 생성)

```python
async def extract_words_and_phrases_sequential(
    chunk_texts: List[str],
    video_id: str
) -> Dict[str, Any]:
    """
    순차적 처리: 단어 추출 완료 후 숙어 추출
    
    Args:
        chunk_texts: 자막 청크 텍스트 리스트
        video_id: 비디오 ID
        
    Returns:
        {
            "words": {...},
            "phrases": {...}
        }
    """
    # 1단계: 단어 추출
    word_result = await extract_words_from_chunks(chunk_texts, video_id)
    
    # 2단계: 숙어 추출
    phrase_result = await extract_phrases_from_chunks(chunk_texts, video_id)
    
    return {
        "words": word_result.get("result", {}),
        "phrases": phrase_result.get("result", {})
    }
```

**장점:**
- 구현 단순
- OOM 위험 최소화
- 현재 코드 재사용 가능

### 5.2 향후: 조건부 병렬 처리 (방안 C)

**설정 추가 (`app/core/config.py`):**
```python
class Settings(BaseSettings):
    # ... 기존 설정 ...
    
    # 병렬 처리 설정
    ENABLE_PARALLEL_WORD_PHRASE_EXTRACTION: bool = False  # MVP: False
    MAX_SAFE_CHUNKS_FOR_PARALLEL: int = 4  # 병렬 처리 안전 청크 수
```

**구현:**
```python
async def extract_words_and_phrases(
    chunk_texts: List[str],
    video_id: str
) -> Dict[str, Any]:
    """
    조건부 병렬 처리: 설정에 따라 순차/병렬 선택
    """
    if (settings.ENABLE_PARALLEL_WORD_PHRASE_EXTRACTION and 
        len(chunk_texts) <= settings.MAX_SAFE_CHUNKS_FOR_PARALLEL):
        return await extract_words_and_phrases_parallel(chunk_texts, video_id)
    else:
        return await extract_words_and_phrases_sequential(chunk_texts, video_id)
```

### 5.3 모니터링 및 최적화

**메트릭 수집:**
- 처리 시간 측정
- 메모리 사용량 모니터링
- OOM 발생 빈도 추적

**최적화 전략:**
1. 실제 사용량 기반으로 `MAX_SAFE_CHUNKS_FOR_PARALLEL` 조정
2. GPU 메모리 여유 시 병렬 처리 활성화
3. 청크 크기 조정 (2000 → 1500 토큰 등)

---

## 📌 결론 및 권장사항

### MVP 단계
- **권장: 순차적 처리 (방안 B)**
- 안정성과 구현 단순성 우선
- 충분한 성능 제공

### 프로덕션 단계
- **권장: 조건부 병렬 처리 (방안 C)**
- 설정 기반으로 유연하게 조정
- 실제 사용량 모니터링 후 최적화

### 고려사항
1. **vLLM 서버의 GPU 메모리 용량 확인**
2. **실제 청크 개수 분포 분석** (평균 몇 개?)
3. **사용자 대기 시간 허용 범위** (10초 vs 5초)
4. **모니터링 시스템 구축** (메모리, 처리 시간)

---

**문서 버전**: 1.0  
**작성일**: 2025-11-26  
**작성자**: 프로젝트 팀

