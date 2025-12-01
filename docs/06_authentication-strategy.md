# 인증 전략 및 JWT 토큰 사용 가이드

LLM 서비스 서버에서 인증을 구현하는 방법과 JWT 토큰 사용 전략에 대한 문서입니다.

---

## 📋 목차

1. [시스템 아키텍처 개요](#1-시스템-아키텍처-개요)
2. [API 키 기반 인증](#2-api-키-기반-인증)
3. [JWT 토큰 기반 인증](#3-jwt-토큰-기반-인증)
4. [인증 구현 위치 및 방법](#4-인증-구현-위치-및-방법)
5. [권장 사항](#5-권장-사항)
   - [5.1 현재 시스템에 맞는 인증 전략](#51-현재-시스템에-맞는-인증-전략)
   - [5.2 보안 고려사항](#52-보안-고려사항)
   - [5.3 구현 우선순위](#53-구현-우선순위)
   - [5.4 API Key vs JWT: 언제 무엇을 사용할까?](#54-api-key-vs-jwt-언제-무엇을-사용할까)

---

## 1. 시스템 아키텍처 개요

### 1.1 전체 구조

```
[사용자] 
  ↓
[프론트엔드 서버] (로그인, 사용자 관리)
  ↓
[백엔드 서버] (비즈니스 로직, 사용자 인증)
  ↓
[LLM 서비스 서버] (현재 서버 - 단어장 생성만 담당)
```

### 1.2 역할 분리

- **프론트엔드 서버**: 사용자 인터페이스, 로그인/회원가입
- **백엔드 서버**: 
  - 사용자 인증/인가 관리
  - 비즈니스 로직 처리
  - LLM 서비스 서버 호출
- **LLM 서비스 서버** (현재 서버):
  - LLM 처리만 담당
  - 단어장 생성 서비스 제공
  - 인증은 백엔드 서버에서 위임받은 토큰 검증만 수행

---

## 2. API 키 기반 인증

### 2.1 API 키 인증이란?

백엔드 서버가 LLM 서비스 서버를 호출할 때 사용하는 인증 방식입니다.

**특징:**
- 서버 간 통신용
- 사용자별로 고유한 API 키 발급
- 데이터베이스에 저장 및 관리

### 2.2 구현 위치

#### 옵션 1: 미들웨어에서 처리 (권장)

```python
# app/core/middleware.py 또는 app/core/auth.py

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logging import get_error_logger

ERROR_LOGGER = get_error_logger()

class APIKeyAuthMiddleware(BaseHTTPMiddleware):
    """API 키 인증 미들웨어"""
    
    async def dispatch(self, request: Request, call_next):
        # 헤더에서 API 키 추출
        api_key = request.headers.get("X-API-Key")
        
        if not api_key:
            ERROR_LOGGER.warning(f"Missing API key - Path: {request.url.path}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API 키가 필요합니다."
            )
        
        # 데이터베이스에서 API 키 검증
        is_valid = await validate_api_key(api_key)
        
        if not is_valid:
            ERROR_LOGGER.warning(f"Invalid API key - Path: {request.url.path}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="유효하지 않은 API 키입니다."
            )
        
        # 요청 처리 계속
        response = await call_next(request)
        return response
```

**장점:**
- 모든 엔드포인트에 자동 적용
- 코드 중복 최소화
- 일관된 인증 처리

#### 옵션 2: 의존성 주입 (Dependency Injection)

```python
# app/core/auth.py

from fastapi import Depends, HTTPException, status, Header
from typing import Optional
from app.core.logging import get_error_logger

ERROR_LOGGER = get_error_logger()

async def validate_api_key(api_key: str) -> bool:
    """API 키 검증 로직"""
    # 데이터베이스 조회
    # 예: SELECT * FROM api_keys WHERE key = ? AND is_active = true
    # ...
    return True  # 또는 False

async def get_api_key(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key")
) -> str:
    """API 키 의존성 함수"""
    if not x_api_key:
        ERROR_LOGGER.warning("Missing API key in request header")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API 키가 필요합니다."
        )
    
    is_valid = await validate_api_key(x_api_key)
    if not is_valid:
        ERROR_LOGGER.warning(f"Invalid API key: {x_api_key[:10]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 API 키입니다."
        )
    
    return x_api_key

# 사용 예시
@router.post("/{video_id}/vocabulary", response_model=VocabularyResponse)
async def post_generate_vocabulary(
    video_id: str,
    api_key: str = Depends(get_api_key)  # 의존성 주입
):
    # api_key는 자동으로 검증됨
    ...
```

**장점:**
- 특정 엔드포인트에만 적용 가능
- 유연한 인증 로직
- 테스트 용이

**단점:**
- 각 엔드포인트마다 `Depends` 추가 필요

### 2.3 데이터베이스 스키마 예시

```sql
-- API 키 테이블
CREATE TABLE api_keys (
    id SERIAL PRIMARY KEY,
    key VARCHAR(255) UNIQUE NOT NULL,
    user_id INTEGER NOT NULL,  -- 백엔드 서버의 사용자 ID
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,  -- 선택사항
    last_used_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 인덱스 추가
CREATE INDEX idx_api_key ON api_keys(key);
CREATE INDEX idx_user_id ON api_keys(user_id);
```

### 2.4 API 키 검증 로직 예시

```python
# app/services/auth_service.py

from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.api_key import APIKey
from datetime import datetime

async def validate_api_key(api_key: str, db: Session) -> bool:
    """API 키 검증"""
    try:
        # 데이터베이스에서 API 키 조회
        key_record = db.query(APIKey).filter(
            APIKey.key == api_key,
            APIKey.is_active == True
        ).first()
        
        if not key_record:
            return False
        
        # 만료 시간 확인 (있는 경우)
        if key_record.expires_at and key_record.expires_at < datetime.now():
            return False
        
        # 마지막 사용 시간 업데이트
        key_record.last_used_at = datetime.now()
        db.commit()
        
        return True
        
    except Exception as e:
        ERROR_LOGGER.error(f"API key validation error: {str(e)}")
        return False
```

---

## 3. JWT 토큰 기반 인증

### 3.1 JWT 토큰이란?

**JWT (JSON Web Token)**는 인증 정보를 포함한 암호화된 토큰입니다.

**구조:**
```
Header.Payload.Signature
```

**예시:**
```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "user_id": 123,
    "email": "user@example.com",
    "exp": 1234567890,
    "iat": 1234567890
  },
  "signature": "암호화된 서명"
}
```

### 3.2 왜 JWT를 사용하는가?

#### ✅ 장점

1. **무상태성 (Stateless)**
   - 서버에 세션 저장 불필요
   - 확장성 향상
   - 여러 서버 간 공유 용이

2. **확장성**
   - 사용자 정보를 토큰에 포함
   - 추가 데이터베이스 조회 최소화
   - 마이크로서비스 아키텍처에 적합

3. **보안**
   - 서명 검증으로 변조 방지
   - 만료 시간 설정 가능
   - 토큰 무효화 가능 (블랙리스트 사용 시)

4. **표준화**
   - 널리 사용되는 표준
   - 다양한 언어/프레임워크 지원

#### ❌ 단점

1. **토큰 크기**
   - 쿠키보다 큰 크기
   - 헤더 크기 제한 고려 필요

2. **무효화 어려움**
   - 토큰 만료 전까지 무효화 불가 (블랙리스트 없이)
   - 로그아웃 시 즉시 무효화 어려움

3. **보안 고려사항**
   - 토큰 탈취 시 재사용 가능
   - HTTPS 필수
   - 짧은 만료 시간 권장

### 3.3 JWT 토큰 사용 시나리오

#### 시나리오 1: 백엔드 서버가 JWT 발급

```
1. 사용자가 프론트엔드에서 로그인
   ↓
2. 프론트엔드 → 백엔드 서버 (로그인 요청)
   ↓
3. 백엔드 서버가 JWT 발급
   ↓
4. 프론트엔드가 JWT 저장 (로컬 스토리지/쿠키)
   ↓
5. 프론트엔드 → 백엔드 서버 (JWT 포함)
   ↓
6. 백엔드 서버가 JWT 검증 후 LLM 서비스 서버 호출
   ↓
7. 백엔드 서버 → LLM 서비스 서버 (API 키 또는 JWT 포함)
```

#### 시나리오 2: LLM 서비스 서버가 JWT 검증

```
1. 백엔드 서버가 JWT를 받아서 LLM 서비스 서버로 전달
   ↓
2. LLM 서비스 서버가 JWT 검증
   - 서명 확인
   - 만료 시간 확인
   - 사용자 정보 추출
   ↓
3. 검증 성공 시 요청 처리
```

### 3.4 JWT 토큰 검증 로직 예시

```python
# app/core/jwt_auth.py

import jwt
from fastapi import HTTPException, status, Header
from typing import Optional
from app.core.config import settings
from app.core.logging import get_error_logger

ERROR_LOGGER = get_error_logger()

def verify_jwt_token(token: str) -> dict:
    """JWT 토큰 검증"""
    try:
        # JWT 디코딩 및 검증
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,  # 백엔드 서버와 동일한 시크릿 키
            algorithms=["HS256"]
        )
        return payload
        
    except jwt.ExpiredSignatureError:
        ERROR_LOGGER.warning("JWT token expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰이 만료되었습니다."
        )
    except jwt.InvalidTokenError:
        ERROR_LOGGER.warning("Invalid JWT token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 토큰입니다."
        )

async def get_current_user(
    authorization: Optional[str] = Header(None)
) -> dict:
    """JWT 토큰에서 사용자 정보 추출"""
    if not authorization:
        ERROR_LOGGER.warning("Missing Authorization header")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증 토큰이 필요합니다."
        )
    
    # "Bearer <token>" 형식에서 토큰 추출
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise ValueError("Invalid scheme")
    except ValueError:
        ERROR_LOGGER.warning("Invalid Authorization header format")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="올바른 인증 형식이 아닙니다. (Bearer <token>)"
        )
    
    # 토큰 검증
    payload = verify_jwt_token(token)
    return payload

# 사용 예시
@router.post("/{video_id}/vocabulary", response_model=VocabularyResponse)
async def post_generate_vocabulary(
    video_id: str,
    current_user: dict = Depends(get_current_user)  # JWT 검증
):
    user_id = current_user.get("user_id")
    # 사용자 정보 활용 가능
    ...
```

### 3.5 JWT 토큰 페이로드 구조 예시

```python
# 백엔드 서버에서 발급하는 JWT 페이로드
{
    "user_id": 123,
    "email": "user@example.com",
    "role": "user",  # user, admin 등
    "exp": 1234567890,  # 만료 시간 (Unix timestamp)
    "iat": 1234567890,  # 발급 시간
    "jti": "unique-token-id"  # 토큰 고유 ID (선택사항)
}
```

### 3.6 JWT 토큰 무효화 (블랙리스트)

```python
# app/services/token_blacklist.py

from datetime import datetime
from app.core.database import get_db
from app.models.token_blacklist import TokenBlacklist

async def is_token_blacklisted(token_id: str, db: Session) -> bool:
    """토큰이 블랙리스트에 있는지 확인"""
    blacklisted = db.query(TokenBlacklist).filter(
        TokenBlacklist.token_id == token_id
    ).first()
    return blacklisted is not None

async def blacklist_token(token_id: str, db: Session):
    """토큰을 블랙리스트에 추가"""
    blacklist_entry = TokenBlacklist(
        token_id=token_id,
        blacklisted_at=datetime.now()
    )
    db.add(blacklist_entry)
    db.commit()
```

---

## 4. 인증 구현 위치 및 방법

### 4.1 권장 구조

```
app/
├── core/
│   ├── auth.py          # 인증 관련 유틸리티
│   ├── jwt_auth.py      # JWT 검증 로직
│   └── middleware.py     # 인증 미들웨어 (선택사항)
├── services/
│   └── auth_service.py  # 인증 서비스 (DB 조회 등)
└── models/
    └── api_key.py       # API 키 모델
```

### 4.2 구현 방법 비교

| 방법 | 적용 위치 | 장점 | 단점 |
|------|----------|------|------|
| 미들웨어 | 모든 요청 | 자동 적용, 코드 중복 최소 | 특정 엔드포인트 제외 어려움 |
| 의존성 주입 | 개별 엔드포인트 | 유연성, 선택적 적용 | 각 엔드포인트마다 추가 필요 |
| 데코레이터 | 개별 엔드포인트 | 간결한 문법 | FastAPI에서는 Depends 권장 |

### 4.3 하이브리드 접근

**권장 방식:**
- 공통 인증: 미들웨어에서 처리
- 추가 검증: 의존성 주입으로 처리

```python
# 미들웨어: 기본 인증 (API 키 또는 JWT 존재 여부)
# 의존성: 세부 검증 (권한 확인, 사용자 정보 추출)
```

---

## 5. 권장 사항

### 5.1 현재 시스템에 맞는 인증 전략

**현재 상황:**
- LLM 서비스 서버는 백엔드 서버에서만 호출됨
- 사용자는 프론트엔드를 통해 접근
- 서버 간 통신이 주 목적

**권장 방식: API 키 기반 인증**

현재 아키텍처에서는 **API 키만으로 충분**합니다.

```
[프론트엔드] → [백엔드 서버] → [비즈니스 처리 백엔드]
                (JWT 검증)      (API Key 검증)
```

**이 구조에서 API Key만으로 충분한 이유:**
- 서버 간 통신만 필요
- 사용자 정보가 비즈니스 처리 백엔드에 필요 없음
- 백엔드 서버가 이미 사용자 인증을 처리함
- 단순히 "인증된 백엔드 서버"인지만 확인하면 됨

**최소 구현 예시:**

```python
# app/core/api_key_auth.py
async def get_api_key(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key")
) -> str:
    """API Key 검증 - 최소 구현"""
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API Key required")
    
    # DB에서 API Key 검증
    is_valid = await validate_api_key(x_api_key)
    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    
    return x_api_key

# app/routes/video.py
@router.post("/{video_id}/vocabulary")
async def post_generate_vocabulary(
    video_id: str,
    api_key: str = Depends(get_api_key)  # 이것만으로 충분
):
    # 비즈니스 로직...
```

### 5.2 보안 고려사항

1. **HTTPS 필수**
   - 모든 통신은 HTTPS로 암호화
   - 토큰/API 키 탈취 방지

2. **토큰 만료 시간**
   - 짧은 만료 시간 설정 (예: 1시간)
   - 리프레시 토큰 사용 고려

3. **API 키 관리**
   - 안전한 저장 (환경 변수, 시크릿 관리 시스템)
   - 정기적인 키 로테이션

4. **에러 메시지**
   - 상세한 에러 정보는 로그에만 기록
   - 사용자에게는 일반적인 메시지 제공

5. **Rate Limiting**
   - API 키 또는 사용자별 요청 제한
   - DDoS 공격 방지

### 5.3 구현 우선순위

1. **1단계: API 키 기반 인증**
   - 간단하고 빠른 구현
   - 서버 간 통신에 충분
   - 현재 프로젝트에 적합

2. **2단계: JWT 토큰 지원 추가**
   - 사용자 정보가 필요한 경우
   - 확장성 요구사항 발생 시
   - (5.4 섹션 참고)

3. **3단계: 고급 기능**
   - 토큰 블랙리스트
   - Rate Limiting
   - 사용자별 권한 관리

### 5.4 API Key vs JWT: 언제 무엇을 사용할까?

#### API Key만으로 충분한 경우

현재 프로젝트와 같은 **서버 간 통신** 구조에서는 API Key만으로 충분합니다.

**특징:**
- 백엔드 서버가 이미 사용자 인증을 처리
- 비즈니스 처리 백엔드는 사용자 정보가 필요 없음
- 단순히 "인증된 서버"인지만 확인하면 됨

**구현:**
- API Key 검증만 수행
- 데이터베이스에서 API Key 존재 여부 확인
- 사용자 정보는 필요 없음

#### JWT가 필요한 구체적인 시나리오

다음과 같은 요구사항이 **실제로 발생할 때** JWT를 추가하는 것을 고려하세요:

##### 시나리오 1: 사용자별 데이터 접근 제어

**예시:** 사용자 A는 자신의 단어장만 볼 수 있어야 함

```
[프론트엔드] → [비즈니스 처리 백엔드]
                (JWT에서 user_id 추출)
                → 사용자별 단어장 필터링
```

**구현:**
```python
@router.get("/vocabularies")
async def get_user_vocabularies(
    current_user: dict = Depends(get_current_user)  # JWT에서 user_id 추출
):
    user_id = current_user["user_id"]
    # user_id로 필터링된 데이터만 반환
    vocabularies = db.query(Vocabulary).filter(Vocabulary.user_id == user_id).all()
    return vocabularies
```

**API Key만으로는:**
- API Key → user_id 매핑을 위해 DB 조회 필요
- 매 요청마다 DB 조회 발생
- JWT는 토큰 자체에 user_id가 포함되어 DB 조회 없이 가능

##### 시나리오 2: 실시간 권한 변경

**예시:** 사용자가 프리미엄으로 업그레이드 → 즉시 권한 반영

```
[프론트엔드] → [백엔드 서버] (권한 변경)
                ↓
[비즈니스 처리 백엔드] (JWT에 최신 권한 정보 포함)
```

**구현:**
```python
# JWT Payload에 권한 정보 포함
{
  "user_id": 123,
  "role": "premium",  # 이 정보가 실시간으로 반영됨
  "exp": 1735689600
}

# 비즈니스 처리 백엔드에서 권한 확인
@router.post("/premium-feature")
async def premium_feature(
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "premium":
        raise HTTPException(status_code=403, detail="Premium required")
    # 프리미엄 기능 제공
```

**API Key만으로는:**
- 권한 변경 시 API Key 재발급 또는 DB 업데이트 필요
- JWT는 토큰 재발급만으로 즉시 반영 가능

##### 시나리오 3: 마이크로서비스 간 직접 통신

**예시:** 서비스 A가 서비스 B를 호출할 때 사용자 정보 전달

```
[비즈니스 처리 백엔드 A] → [비즈니스 처리 백엔드 B]
                            (JWT로 사용자 정보 전달)
```

**구현:**
```python
# 서비스 A가 서비스 B를 호출할 때
async def call_service_b(user_jwt: str):
    headers = {"Authorization": f"Bearer {user_jwt}"}
    response = await httpx.post(
        "https://service-b/api/data",
        headers=headers
    )
    # 서비스 B는 JWT에서 사용자 정보를 직접 추출
```

**API Key만으로는:**
- 서비스 간 사용자 정보 전달이 어려움
- JWT는 사용자 정보를 포함해 전달 가능

##### 시나리오 4: 사용량 추적 및 과금

**예시:** 사용자별 API 호출 횟수 추적

```
[비즈니스 처리 백엔드]
  - JWT에서 user_id 추출
  - 사용자별 호출 횟수 카운트
  - 과금 정보 업데이트
```

**구현:**
```python
@router.post("/{video_id}/vocabulary")
async def post_generate_vocabulary(
    video_id: str,
    current_user: dict = Depends(get_current_user)  # JWT에서 user_id
):
    user_id = current_user["user_id"]
    
    # 사용자별 사용량 추적
    usage = db.query(Usage).filter(Usage.user_id == user_id).first()
    usage.call_count += 1
    db.commit()
    
    # 과금 처리
    if usage.call_count > usage.plan_limit:
        raise HTTPException(status_code=402, detail="Usage limit exceeded")
    
    # 비즈니스 로직...
```

**API Key만으로는:**
- API Key → user_id 매핑을 위해 DB 조회 필요
- JWT는 토큰에서 직접 추출 가능

##### 시나리오 5: 다중 서버 환경에서 세션 공유 불가

**예시:** 여러 서버에서 세션 저장소 없이 인증

```
[서버 1] ← 사용자 요청
[서버 2] ← 사용자 요청 (다른 서버)
[서버 3] ← 사용자 요청 (또 다른 서버)

→ 세션 저장소 없이도 모든 서버에서 인증 가능
```

**구현:**
```python
# 서버 1, 2, 3 모두 동일한 JWT_SECRET_KEY 사용
# 세션 저장소 없이도 JWT 검증 가능
def verify_jwt_token(token: str) -> dict:
    payload = jwt.decode(
        token,
        settings.JWT_SECRET_KEY,  # 모든 서버가 동일한 키 사용
        algorithms=["HS256"]
    )
    return payload  # DB 조회 없이 사용자 정보 추출
```

**API Key만으로는:**
- API Key 검증은 가능하지만, 사용자 정보는 DB 조회 필요
- JWT는 토큰 자체에 사용자 정보 포함

#### JWT를 추가해야 하는 시점

다음 요구사항이 **실제로 발생할 때** 고려하세요:

- ✅ 사용자별 단어장 저장 및 조회 기능
- ✅ 사용자별 사용량 추적 및 과금
- ✅ 프리미엄/일반 사용자 권한 구분
- ✅ 사용자별 설정 저장 기능
- ✅ 마이크로서비스 간 사용자 정보 전달

**이런 요구사항이 없으면 API Key만으로 시작하고, 필요할 때 JWT를 추가하는 것이 합리적입니다.**

---

## 결론

현재 LLM 서비스 서버의 역할(백엔드 서버에서만 호출)을 고려할 때:

1. **초기 구현**: **API 키 기반 인증만으로 충분** (의존성 주입 권장)
2. **확장 시**: JWT 토큰 지원 추가 (5.4 섹션의 시나리오 발생 시)
3. **보안**: HTTPS 필수, 에러 메시지 최소화, Rate Limiting 고려

**핵심 원칙:**
- 현재 요구사항에 맞는 최소한의 구현
- 오버엔지니어링 방지
- 실제 필요할 때 JWT 추가

인증은 **의존성 주입**을 통해 처리하는 것을 권장하며, 모든 엔드포인트에 자동 적용이 필요한 경우 **미들웨어**를 함께 사용하는 하이브리드 접근이 가장 유연합니다.

