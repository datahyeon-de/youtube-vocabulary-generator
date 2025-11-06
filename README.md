# 유튜브 자막 기반 영어 단어장 생성 서비스

유튜브 영상의 자막을 추출하여 사용자의 니즈에 맞는 도메인별 영어 단어장을 자동 생성하는 서비스입니다.

## 🎯 프로젝트 목표

사용자가 제공한 유튜브 영상의 자막을 추출하여, 사용자의 니즈(학생 단어 공부, 직장인 영어 공부 등)에 맞는 도메인별 영어 단어장을 자동 생성합니다.

## ✨ 주요 기능

1. 유튜브 영상 링크 입력 및 검증
2. 자막 데이터 추출
3. LLM을 활용한 도메인별 단어 선별 및 한국어 뜻 생성
4. 단어장 생성 및 제공

## 🏗️ 프로젝트 구조

```
youtube-vocabulary-generator/
├── README.md
├── requirements.txt
├── .gitignore
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI 메인 서버
│   ├── routes/
│   │   ├── __init__.py
│   │   └── video.py            # 비디오 관련 엔드포인트
│   ├── services/
│   │   ├── __init__.py
│   │   ├── validator.py        # 링크 검증
│   │   ├── transcript.py        # 자막 추출
│   │   └── llm_processor.py     # LLM 처리 (또는 별도 서버)
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py          # Pydantic 스키마
│   └── templates/              # HTML 템플릿 (필요시)
├── llm_server/                 # 별도 LLM 서버 (옵션)
│   ├── main.py
│   └── models/
└── tests/
    ├── __init__.py
    └── test_*.py
```

## 🚀 시작하기

### 필수 요구사항

- Python 3.8 이상
- pip

### 설치 방법

```bash
# 의존성 설치
pip install -r requirements.txt
```

### 실행 방법

```bash
# 서버 실행 (Phase 2 이후 적용 예정)
uvicorn app.main:app --reload
```

## 📝 개발 단계

이 프로젝트는 단계별로 개발됩니다:

- **Phase 1**: 프로젝트 초기 설정 및 레포지터리 구성 ✅
- **Phase 2**: FastAPI 서버 및 입력 검증 시스템
- **Phase 3**: 자막 추출 서비스
- **Phase 4**: LLM 처리 서버 구축
- **Phase 5**: 단어장 생성 및 응답
- **Phase 6**: 통합 및 엔드투엔드 테스트

자세한 내용은 프로젝트 계획서를 참고하세요.

## 📄 라이선스

이 프로젝트는 개발 중입니다.

