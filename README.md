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
├── .cursor/
│   ├── project-plan.md
│   ├── commands/
│   │   └── commands.yaml
│   └── rules/
│       └── rules.mdc
├── .github/
│   ├── ISSUE_TEMPLATE/
│   └── PULL_REQUEST_TEMPLATE/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI 메인 서버 (로깅, 미들웨어 등록)
│   ├── core/
│   │   ├── logging.py          # 로깅 설정
│   │   └── middleware.py       # 요청/응답 로깅 미들웨어
│   ├── routes/
│   │   ├── __init__.py
│   │   └── video.py            # 비디오 관련 엔드포인트
│   ├── services/
│   │   ├── __init__.py
│   │   ├── validator.py        # 링크 검증 및 Video ID 추출
│   │   └── transcript.py       # YouTube 자막 추출 및 청크 생성
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py          # Pydantic 스키마
│   └── templates/              # HTML 템플릿 (필요시)
├── llm_server/                 # 향후 확장용 (옵션)
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── test_main.py
    ├── test_models/
    ├── test_routes/
    └── test_services/
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

## 🛠️ Cursor 명령 가이드

`.cursor/commands/commands.yaml`에 정의된 명령을 활용하면 프로젝트 계획과 문서를 일관되게 관리할 수 있습니다.

| 명령 | 설명 | 주요 활용 |
|------|------|-----------|
| `init_project` | 기본 폴더 및 템플릿 구조 생성 | 신규 환경 초기화 |
| `show_plan` | 프로젝트 전체 계획 보기 | 현황 공유/점검 |
| `sync_plan` | 계획 상태 동기화 | 체크박스 업데이트 |
| `current_phase` | 진행 중 Phase 확인 | 다음 단계 파악 |
| `next_phase` | Phase 전환 표시 | 진행 상황 기록 |
| `next_task` | Task 전환 표시 | 세부 작업 추적 |
| `update_readme` | README 동기화 | 진행 내역 반영 |

- 명령 실행 뒤에는 `.cursor/project-plan.md`와 README 변경 사항을 커밋 전에 확인하세요.
- 프로젝트 협업 규칙은 `.cursor/rules/rules.mdc`에 정리되어 있습니다.

## 📝 개발 단계

이 프로젝트는 단계별로 개발됩니다:

- **Phase 1**: 프로젝트 초기 설정 및 레포지터리 구성 ✅
- **Phase 2**: FastAPI 서버 및 입력 검증 시스템 ✅
- **Phase 3**: 자막 추출 서비스 ✅
- **Phase 4**: LLM 처리 서버 구축 ⏳
- **Phase 5**: 단어장 생성 및 응답
- **Phase 6**: 통합 및 엔드투엔드 테스트

자세한 내용은 프로젝트 계획서를 참고하세요.

## 🤝 기여하기

프로젝트에 기여하고 싶으시다면 [CONTRIBUTING.md](CONTRIBUTING.md)를 참고하세요.  
브랜치 네이밍, 커밋 메시지, 이슈 작성 가이드가 포함되어 있습니다.

## 📄 라이선스

이 프로젝트는 개발 중입니다.

