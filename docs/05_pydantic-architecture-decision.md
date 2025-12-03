# 서비스 레이어 Pydantic 사용 여부 아키텍처 결정

서비스 레이어에서 Pydantic을 사용하지 않고 딕셔너리를 사용한 이유와 그로 인한 장단점, 그리고 Pydantic으로 전환 시 고려사항에 대한 문서입니다.

---

## 📋 목차

1. [현재 구조](#1-현재-구조)
2. [서비스 레이어에서 Pydantic을 사용하지 않은 이유](#2-서비스-레이어에서-pydantic을-사용하지-않은-이유)
3. [딕셔너리 사용의 장점과 단점](#3-딕셔너리-사용의-장점과-단점)
4. [Pydantic으로 전환 시 장점과 유의할 점](#4-pydantic으로-전환-시-장점과-유의할-점)
5. [권장 사항](#5-권장-사항)

---

## 1. 현재 구조

### 1.1 서비스 레이어 (딕셔너리 사용)

```python
# app/services/llm/processor.py
async def process_vocabulary(
    chunk_texts: List[str],
    video_id: str
) -> Dict[str, Any]:
    """전체 워크플로우를 통합하여 자막 청크에서 단어장을 생성합니다."""
    # ... 처리 로직
    return {
        "videoId": video_id,
        "words": [
            {
                "word": "word1",
                "pos": "n",
                "meanings": ["뜻1", "뜻2"],
                "synonyms": ["synonym1"],
                "example": "Example sentence."
            }
        ],
        "phrases": [...]
    }
```

### 1.2 API 레이어 (Pydantic 사용)

```python
# app/models/schemas.py
class WordEntry(BaseModel):
    word: str
    pos: str
    meanings: List[str]
    synonyms: List[str]
    example: str

class VocabularyResponse(BaseModel):
    video_id: str
    words: List[WordEntry]
    phrases: List[PhraseEntry]
    status: str = "success"
    message: str | None = None

# app/routes/video.py
@router.post("/{video_id}/vocabulary", response_model=VocabularyResponse)
async def post_vocabulary(...):
    result = await process_vocabulary(...)
    # 딕셔너리를 Pydantic 모델로 변환
    return VocabularyResponse(**result)
```

---

## 2. 서비스 레이어에서 Pydantic을 사용하지 않은 이유

### 2.1 LLM 응답의 불확실성

**문제점:**
- LLM 응답은 항상 예상한 형식으로 오지 않을 수 있음
- JSON 파싱은 성공하지만 필드가 누락되거나 형식이 다를 수 있음
- 예: `meanings`가 리스트가 아닌 문자열로 올 수 있음

**딕셔너리 사용 시:**
```python
# 유연한 처리 가능
meanings = word_data.get("meanings", [])
if not isinstance(meanings, list):
    meanings = [meanings] if meanings else []
```

**Pydantic 사용 시:**
```python
# 필드가 없거나 형식이 다르면 ValidationError 발생
# 부분 실패 처리 어려움
word_entry = WordEntry(**word_data)  # ValidationError 가능
```

### 2.2 부분 실패 처리

**현재 구조:**
```python
# 1단계에서 일부 청크 실패 시 빈 딕셔너리로 대체 가능
if isinstance(word_extraction_result, Exception):
    word_extraction_result = {"videoId": video_id, "result": {}}
    # 다음 단계 계속 진행 가능
```

**Pydantic 사용 시:**
```python
# 필수 필드가 없으면 모델 생성 불가
# 부분 실패 시 전체 프로세스 중단 가능성
```

### 2.3 성능 고려

**딕셔너리:**
- 가벼운 데이터 구조
- 변환 오버헤드 없음
- JSON 파싱 후 바로 사용 가능

**Pydantic:**
- 모델 인스턴스 생성 비용
- 검증 로직 실행 비용
- 대량 데이터 처리 시 성능 저하 가능

### 2.4 단계별 데이터 변환

**현재 워크플로우:**
```
1단계: LLM JSON 응답 → 딕셔너리 (JSON 파싱)
2단계: 딕셔너리 → 딕셔너리 (병합 및 변환)
3단계: 딕셔너리 → 딕셔너리 (최종 형식)
API: 딕셔너리 → Pydantic 모델 (검증 및 직렬화)
```

각 단계에서 딕셔너리를 사용하면 중간 변환 비용이 없음

---

## 3. 딕셔너리 사용의 장점과 단점

### 3.1 장점

#### ✅ 유연성
- LLM 응답의 다양한 형식 처리 가능
- 필드 누락, 타입 불일치 등에 유연하게 대응
- 부분 실패 시 빈 딕셔너리로 대체 가능

#### ✅ 성능
- 가벼운 데이터 구조
- 변환 오버헤드 없음
- JSON 파싱 후 바로 사용 가능

#### ✅ 단순성
- 복잡한 검증 로직 불필요
- 단계별 데이터 변환 용이
- 디버깅 시 데이터 구조 확인 쉬움

#### ✅ 부분 실패 처리
```python
# 일부 청크 실패해도 나머지 처리 가능
if isinstance(result, Exception):
    result = {"videoId": video_id, "result": {}}
    # 다음 단계 계속 진행
```

### 3.2 단점

#### ❌ 타입 안전성 부족
- IDE 자동완성 지원 제한
- 런타임에만 타입 오류 발견 가능
- 타입 힌팅이 `Dict[str, Any]`로 제한적

#### ❌ 검증 부재
- 필드 존재 여부, 타입 검증 수동 처리 필요
- 잘못된 데이터가 다음 단계로 전달 가능
- API 레이어에서만 최종 검증

#### ❌ 필드명 불일치 가능성
```python
# 서비스 레이어: camelCase
{"videoId": "abc", "words": [...]}

# API 레이어: snake_case
{"video_id": "abc", "words": [...]}
```

#### ❌ 문서화 부족
- 서비스 레이어 반환 형식이 코드에만 존재
- API 문서에 반영되지 않음
- 팀원 간 소통 시 문서 부재

---

## 4. Pydantic으로 전환 시 장점과 유의할 점

### 4.1 장점

#### ✅ 타입 안전성
```python
# IDE 자동완성 지원
result: VocabularyResponse = await process_vocabulary(...)
result.words[0].meanings  # 자동완성 가능
```

#### ✅ 자동 검증
- 필드 타입, 필수 여부 자동 검증
- 잘못된 데이터 조기 발견
- 명확한 에러 메시지

#### ✅ 일관성
- 서비스 레이어와 API 레이어 동일한 모델 사용
- 필드명 일관성 보장
- 타입 일관성 보장

#### ✅ 문서화
- 모델 정의 자체가 문서
- OpenAPI 스키마 자동 생성 가능
- 팀원 간 소통 용이

### 4.2 유의할 점

#### ⚠️ LLM 응답 변환 시 오류 처리

**문제:**
```python
# LLM 응답이 예상과 다를 수 있음
word_data = {"word": "example", "meanings": "뜻1"}  # meanings가 리스트 아님
word_entry = WordEntry(**word_data)  # ValidationError 발생
```

**해결 방안:**
```python
# 1. 유연한 검증 로직 추가
class WordEntry(BaseModel):
    meanings: List[str]
    
    @field_validator('meanings', mode='before')
    @classmethod
    def normalize_meanings(cls, v):
        if isinstance(v, str):
            return [v]
        if isinstance(v, list):
            return v
        return []

# 2. try-except로 감싸기
try:
    word_entry = WordEntry(**word_data)
except ValidationError:
    # 빈 값으로 대체하거나 기본값 사용
    word_entry = WordEntry(word="", pos="", meanings=[], ...)
```

#### ⚠️ 부분 실패 처리 복잡도 증가

**현재:**
```python
# 빈 딕셔너리로 쉽게 대체
if isinstance(result, Exception):
    result = {"videoId": video_id, "result": {}}
```

**Pydantic 사용 시:**
```python
# 필수 필드가 있어야 모델 생성 가능
if isinstance(result, Exception):
    result = VocabularyResponse(
        video_id=video_id,
        words=[],  # 필수 필드
        phrases=[]  # 필수 필드
    )
```

#### ⚠️ 성능 오버헤드

**고려사항:**
- 대량 데이터 처리 시 모델 생성 비용
- 검증 로직 실행 비용
- 메모리 사용량 증가

**최적화 방안:**
```python
# 1. 검증 모드 선택
class Config:
    validate_assignment = False  # 할당 시 재검증 비활성화

# 2. 대량 데이터는 배치 처리
words = [WordEntry(**w) for w in words_data]  # 리스트 컴프리헨션 사용
```

#### ⚠️ 필드명 변환 필요

**문제:**
- LLM 응답: `{"videoId": "abc"}` (camelCase)
- Pydantic 모델: `{"video_id": "abc"}` (snake_case)

**해결 방안:**
```python
# 1. 별칭 사용
class VocabularyResponse(BaseModel):
    video_id: str = Field(alias="videoId")
    
    class Config:
        populate_by_name = True  # videoId와 video_id 모두 허용

# 2. 변환 함수 사용
def convert_camel_to_snake(data: dict) -> dict:
    # camelCase → snake_case 변환
    ...
```

#### ⚠️ 선택적 필드 처리

**문제:**
- LLM 응답에서 일부 필드가 누락될 수 있음
- Pydantic은 필수 필드가 없으면 ValidationError 발생

**해결 방안:**
```python
# 모든 필드를 선택적으로 만들기
class WordEntry(BaseModel):
    word: str = ""
    pos: str = ""
    meanings: List[str] = []
    synonyms: List[str] = []
    example: str = ""
```

---

## 5. 권장 사항

### 5.1 현재 구조 유지 (권장)

**이유:**
- LLM 응답의 불확실성 대응
- 부분 실패 처리 용이
- 성능 최적화
- 단계별 데이터 변환 용이

**API 레이어에서 변환:**
```python
@router.post("/{video_id}/vocabulary", response_model=VocabularyResponse)
async def post_vocabulary(...):
    result = await process_vocabulary(chunk_texts, video_id)
    
    # 딕셔너리를 Pydantic 모델로 변환
    return VocabularyResponse(
        video_id=result["videoId"],
        words=[WordEntry(**word) for word in result["words"]],
        phrases=[PhraseEntry(**phrase) for phrase in result["phrases"]],
        status="success"
    )
```

### 5.2 Pydantic 전환 시 고려사항

**전환 조건:**
- LLM 응답이 안정적이고 일관적일 때
- 타입 안전성이 중요한 경우
- 팀 내 타입 안전성 우선순위가 높을 때

**전환 시 필수 작업:**
1. 유연한 검증 로직 추가 (`field_validator` 사용)
2. 부분 실패 처리 로직 개선
3. 필드명 변환 로직 추가 (camelCase ↔ snake_case)
4. 성능 테스트 및 최적화
5. 에러 핸들링 강화

### 5.3 하이브리드 접근

**제안:**
- 서비스 레이어: 딕셔너리 유지 (유연성)
- API 레이어: Pydantic 사용 (검증 및 문서화)
- 내부 유틸리티: Pydantic 모델 사용 (타입 안전성)

```python
# 내부 유틸리티 함수
def validate_word_entry(data: dict) -> WordEntry:
    """딕셔너리를 WordEntry로 변환 (검증 포함)"""
    try:
        return WordEntry(**data)
    except ValidationError:
        # 기본값으로 대체
        return WordEntry(
            word=data.get("word", ""),
            pos=data.get("pos", ""),
            meanings=data.get("meanings", []),
            ...
        )
```

---

## 결론

현재 구조(서비스 레이어는 딕셔너리, API 레이어는 Pydantic)는 다음과 같은 이유로 적절합니다:

1. **LLM 응답의 불확실성**: 딕셔너리로 유연하게 처리
2. **부분 실패 처리**: 빈 딕셔너리로 쉽게 대체 가능
3. **성능**: 변환 오버헤드 최소화
4. **API 검증**: API 레이어에서 Pydantic으로 최종 검증

Pydantic으로 전환을 고려한다면, LLM 응답의 안정성이 확보된 후 단계적으로 진행하는 것을 권장합니다.

