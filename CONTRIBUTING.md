# 기여 가이드 (Contributing Guide)

이 문서는 프로젝트에 기여하기 위한 브랜치 네이밍, 커밋 메시지, 이슈 작성 가이드입니다.

## 📋 목차

1. [이슈 작성](#이슈-작성)
   - [이슈 템플릿 사용 방법](#이슈-템플릿-사용-방법)
   - [템플릿별 상세 가이드](#템플릿별-상세-가이드)
   - [이슈 템플릿 활용 팁](#이슈-템플릿-활용-팁)
2. [브랜치 네이밍](#브랜치-네이밍)
3. [커밋 메시지](#커밋-메시지)
4. [작업 흐름 예시](#작업-흐름-예시)

---

## 🎯 이슈 작성

이슈를 생성할 때는 GitHub 이슈 템플릿을 사용하세요. 각 템플릿은 자동으로 올바른 접두사를 포함합니다.

### 이슈 템플릿 사용 방법

1. **GitHub 저장소에서 이슈 생성**
   - 저장소 페이지에서 `Issues` 탭 클릭
   - `New issue` 버튼 클릭
   - 작업 유형에 맞는 템플릿 선택

2. **템플릿 선택 가이드**
   - 새로운 기능 추가 → `기능 개발` 템플릿
   - 버그 수정 또는 기존 기능 개선 → `기능 수정` 템플릿
   - 문서 작성/수정 → `문서 작업` 템플릿
   - 설정 파일 추가/수정 → `설정 파일 업로드` 템플릿

3. **템플릿 작성 팁**
   - 각 섹션의 주석(<!-- -->)을 참고하여 필요한 정보만 작성
   - 체크리스트는 작업 진행 상황을 추적하는 데 활용
   - 관련 정보가 없으면 해당 섹션은 비워둬도 됨

### 이슈 제목 작성 방법

템플릿을 선택하면 제목 필드에 자동으로 접두사가 추가됩니다. 접두사 뒤에 설명만 추가하면 됩니다.

**제목 작성 규칙:**
- 접두사는 템플릿이 자동으로 추가 (`[FEAT]`, `[FIX]`, `[DOCS]`, `[CHORE]`)
- 접두사 뒤에 **간단하고 명확한 설명** 추가
- 50자 이내로 작성 (가독성 향상)
- 현재형으로 작성 (과거형 사용 지양)
- 동사로 시작하는 것을 권장

**좋은 제목 예시:**
```
[FEAT] FastAPI user input endpoint
[FEAT] Add YouTube link validation
[FIX] YouTube link validation error
[FIX] Handle empty transcript error
[DOCS] Update installation guide
[DOCS] Add API endpoints documentation
[CHORE] Add Docker Compose config
[CHORE] Update GitHub Actions workflow
```

**나쁜 제목 예시:**
```
[FEAT] FastAPI user input endpoint 개발  # "개발" 같은 불필요한 단어
[FEAT] Added FastAPI user input endpoint  # 과거형 사용
[FEAT] FastAPI user input endpoint for YouTube link validation and transcript extraction  # 너무 김
[FEAT] fastapi user input endpoint  # 첫 글자 대문자 누락
```

**제목 작성 팁:**
1. **구체적으로**: 무엇을 하는지 명확히 표현
   - 좋음: `FastAPI user input endpoint`
   - 나쁨: `새 기능 추가`
2. **간결하게**: 핵심만 포함
   - 좋음: `YouTube link validation`
   - 나쁨: `YouTube 링크를 검증하는 기능을 추가합니다`
3. **영문으로**: 일관성 유지 (프로젝트 정책에 따라 다를 수 있음)
4. **동사로 시작**: "Add", "Update", "Fix", "Implement" 등

### 이슈 접두사

| 작업 유형 | 이슈 접두사 | 템플릿 이름 | 예시 |
|---------|-----------|----------|------|
| 기능 개발 | `[FEAT]` | 기능 개발 | `[FEAT] FastAPI user input endpoint` |
| 기능 수정/버그 수정 | `[FIX]` | 기능 수정 | `[FIX] YouTube link validation error` |
| 문서 작업 | `[DOCS]` | 문서 작업 | `[DOCS] Update installation guide` |
| 설정 파일 | `[CHORE]` | 설정 파일 업로드 | `[CHORE] Add Docker Compose config` |

### 템플릿별 상세 가이드

#### 📦 기능 개발 템플릿 (`feature-development.md`)

**언제 사용하나요?**
- 새로운 기능을 추가할 때
- API 엔드포인트를 새로 만들 때
- 새로운 서비스나 유틸리티를 구현할 때

**작성 방법:**
1. **기능 개요**: 개발할 기능을 한 문장으로 요약
   ```
   예: YouTube 링크를 입력받아 자막을 추출하는 FastAPI 엔드포인트 개발
   ```

2. **목표**: 이 기능으로 달성하고자 하는 목표 명시
   ```
   예: 사용자가 YouTube URL을 입력하면 자동으로 자막을 추출하여 단어장을 생성할 수 있도록 함
   ```

3. **작업 내용**: 구현해야 할 구체적인 작업 나열
   ```
   - [ ] FastAPI 엔드포인트 생성
   - [ ] YouTube URL 검증 로직 구현
   - [ ] 자막 추출 기능 연동
   ```

4. **체크리스트 활용**: 작업 진행 상황을 체크박스로 관리
   - 설계 단계: 요구사항 분석, 기술 스택 결정
   - 개발 단계: 코드 구현, 에러 핸들링
   - 테스트 단계: 단위 테스트, 통합 테스트
   - 문서화 및 배포: 코드 주석, README 업데이트

**실제 사용 예시:**
```markdown
## 📋 기능 개요
YouTube 링크를 입력받아 자막을 추출하는 FastAPI 엔드포인트 개발

## 🎯 목표
사용자가 YouTube URL을 입력하면 자동으로 자막을 추출하여 단어장을 생성할 수 있도록 함

## 📝 작업 내용
- [ ] POST /api/extract-transcript 엔드포인트 생성
- [ ] YouTube URL 검증 로직 구현
- [ ] yt-dlp를 사용한 자막 추출 기능 연동
- [ ] 에러 핸들링 및 응답 형식 정의
```

#### 🔧 기능 수정 템플릿 (`feature-modification.md`)

**언제 사용하나요?**
- 버그를 발견했을 때
- 기존 기능을 개선해야 할 때
- 성능 최적화가 필요할 때
- 에러 처리를 개선해야 할 때

**작성 방법:**
1. **문제 설명**: 발생한 문제를 명확하게 설명
   ```
   예: YouTube Shorts URL을 입력하면 검증 오류가 발생함
   ```

2. **재현 방법**: 문제를 재현하는 단계별 방법 작성
   ```
   1. POST /api/extract-transcript 요청
   2. YouTube Shorts URL 입력 (예: https://youtube.com/shorts/abc123)
   3. 400 Bad Request 에러 발생
   ```

3. **예상 결과**: 수정 후 기대되는 결과
   ```
   예: YouTube Shorts URL도 정상적으로 처리되어 자막이 추출됨
   ```

4. **관련 정보**: 문제가 발생한 파일과 라인 번호 명시
   ```
   - 파일: app/services/validator.py
   - 라인: 45-50
   ```

**실제 사용 예시:**
```markdown
## 🐛 문제 설명
YouTube Shorts URL을 입력하면 검증 오류가 발생하여 자막 추출이 불가능함

## 🔍 재현 방법
1. POST /api/extract-transcript 엔드포인트 호출
2. YouTube Shorts URL 입력: https://youtube.com/shorts/abc123
3. 400 Bad Request 에러 발생 확인

## 💡 예상 결과
YouTube Shorts URL도 정상적으로 검증되어 자막이 추출됨

## 📝 수정 내용
- [ ] validator.py의 URL 검증 로직 수정
- [ ] Shorts URL 패턴 추가
- [ ] 관련 테스트 케이스 추가
```

#### 📚 문서 작업 템플릿 (`documentation.md`)

**언제 사용하나요?**
- README나 다른 문서를 작성/수정할 때
- API 문서를 업데이트할 때
- 설치 가이드를 추가할 때
- 코드 예제를 문서화할 때

**작성 방법:**
1. **문서 개요**: 작업 유형과 문서명 명시
   ```
   - 작업 유형: 수정
   - 문서명: README.md
   ```

2. **작업 내용**: 구체적인 문서 작업 내용
   ```
   - [ ] 설치 방법 섹션 추가
   - [ ] API 사용 예제 추가
   - [ ] 환경 변수 설정 가이드 추가
   ```

3. **문서 정보**: 문서 경로와 대상 섹션 명시
   ```
   - 문서 경로: /README.md
   - 대상 섹션: 설치 및 실행 섹션
   ```

**실제 사용 예시:**
```markdown
## 📚 문서 개요
- 작업 유형: 수정
- 문서명: README.md

## 📝 작업 내용
- [ ] FastAPI 서버 실행 방법 추가
- [ ] 환경 변수 설정 가이드 추가
- [ ] API 엔드포인트 사용 예제 추가

## 📄 문서 정보
- 문서 경로: /README.md
- 대상 섹션: 설치 및 실행
```

#### ⚙️ 설정 파일 업로드 템플릿 (`configuration.md`)

**언제 사용하나요?**
- Docker Compose 파일 추가
- CI/CD 설정 파일 추가/수정
- 환경 변수 설정 파일 관리
- 의존성 파일 업데이트

**작성 방법:**
1. **설정 파일 개요**: 파일명과 작업 유형
   ```
   - 파일명: docker-compose.yml
   - 작업 유형: 추가
   ```

2. **보안 확인**: 민감한 정보가 포함되어 있는지 확인
   - API 키, 비밀번호 등은 환경 변수로 관리
   - `.gitignore`에 추가해야 할 파일 확인

3. **관련 파일 정보**: 영향 범위 명시
   ```
   - 파일 경로: /docker-compose.yml
   - 영향 범위: 개발 환경 설정
   ```

**실제 사용 예시:**
```markdown
## ⚙️ 설정 파일 개요
- 파일명: docker-compose.yml
- 작업 유형: 추가

## 📝 작업 내용
- [ ] FastAPI 서비스 컨테이너 설정
- [ ] PostgreSQL 데이터베이스 컨테이너 설정
- [ ] 볼륨 마운트 설정

## 🔐 보안 확인
- [x] 민감한 정보 포함 여부 확인 (없음)
- [x] .gitignore로 관리 필요 여부 확인 (불필요)
- [x] 환경 변수로 관리해야 할 항목 확인 (데이터베이스 비밀번호)
```

### 이슈 템플릿 활용 팁

1. **체크리스트 관리**
   - 작업을 시작할 때 체크리스트를 확인하며 계획 수립
   - 각 단계를 완료할 때마다 체크박스 체크
   - PR 생성 시 완료된 체크리스트를 스크린샷으로 첨부하면 리뷰어가 진행 상황 파악 용이

2. **브랜치 및 커밋 가이드 활용**
   - 각 템플릿 상단에 브랜치명과 커밋 메시지 가이드가 포함되어 있음
   - 이슈 생성 후 가이드를 참고하여 브랜치 생성 및 커밋

3. **관련 정보 섹션 활용**
   - 관련 코드, 문서, 이전 이슈/PR을 링크하면 컨텍스트 이해에 도움
   - GitHub에서 `#이슈번호` 형식으로 이슈를 참조 가능

4. **체크리스트 커스터마이징**
   - 각 프로젝트에 맞게 체크리스트 항목 추가/수정 가능
   - 팀 내에서 자주 놓치는 항목을 체크리스트에 추가하면 실수 방지

### 이슈 작성 체크리스트

이슈를 생성하기 전에 다음을 확인하세요:

**제목 작성:**
- [ ] 적절한 템플릿 선택 (템플릿이 접두사를 자동으로 추가)
- [ ] 제목에 접두사 뒤에 간단하고 명확한 설명 추가
- [ ] 제목이 50자 이내로 작성되었는지 확인
- [ ] 현재형으로 작성 (과거형 사용 지양)
- [ ] 첫 글자 대문자 사용

**내용 작성:**
- [ ] 필수 정보 작성 (기능 개요, 문제 설명 등)
- [ ] 체크리스트 항목 확인
- [ ] 관련 이슈/PR 링크 (있는 경우)
- [ ] 라벨 지정 (템플릿이 자동으로 추가)

**제목 작성 예시:**
- ✅ 좋은 예: `[FEAT] FastAPI user input endpoint`
- ❌ 나쁜 예: `[FEAT] FastAPI user input endpoint 개발` (불필요한 단어)
- ❌ 나쁜 예: `[FEAT] Added FastAPI user input endpoint` (과거형)

---

## 🌿 브랜치 네이밍

브랜치명은 작업 유형과 간단한 설명으로 구성합니다.

### 형식

```
{타입}/{간단한-설명}
```

### 브랜치 타입

| 타입 | 설명 | 예시 |
|-----|------|------|
| `feat` | 새로운 기능 개발 | `feat/fastapi-user-input` |
| `fix` | 버그 수정 또는 기능 수정 | `fix/youtube-link-validation` |
| `docs` | 문서 작업 | `docs/readme-installation` |
| `chore` | 설정 파일, 빌드 도구 등 | `chore/docker-compose-setup` |
| `refactor` | 코드 리팩토링 (기능 변경 없음) | `refactor/extract-validator-service` |
| `test` | 테스트 추가 또는 수정 | `test/user-input-validation` |

### 브랜치명 작성 규칙

- 소문자 사용
- 하이픈(`-`)으로 단어 구분
- 간결하고 명확하게 작성
- 이슈 번호를 포함할 수도 있음: `feat/#123-fastapi-user-input`

---

## 💬 커밋 메시지

[Conventional Commits](https://www.conventionalcommits.org/) 스펙을 따릅니다.

### 형식

```
{타입}: {간단한 설명}

{상세 설명 (선택사항)}

{이슈 번호 (선택사항)}
```

### 커밋 타입

| 타입 | 설명 | 예시 |
|-----|------|------|
| `feat` | 새로운 기능 | `feat: Add FastAPI user input endpoint` |
| `fix` | 버그 수정 | `fix: Correct YouTube link validation logic` |
| `docs` | 문서 변경 | `docs: Update installation guide` |
| `chore` | 설정 파일, 빌드 도구 | `chore: Add Docker Compose configuration` |
| `refactor` | 코드 리팩토링 | `refactor: Extract validator service` |
| `test` | 테스트 추가/수정 | `test: Add unit tests for user input` |
| `style` | 코드 포맷팅 (기능 변경 없음) | `style: Format code with black` |

### 커밋 메시지 작성 규칙

- 첫 줄은 50자 이내로 작성
- 메시지는 현재형으로 작성 (Add, Fix, Update 등)
- 첫 글자는 대문자, 나머지는 소문자 (단, 고유명사는 제외)
- 문장 끝에 마침표(.) 사용하지 않음
- 상세 설명은 각 줄을 72자 이내로 작성

### 예시

```bash
# 좋은 예시
feat: Add YouTube link validation endpoint
fix: Handle empty transcript error
docs: Update README with installation steps

# 나쁜 예시
feat: added youtube link validation  # 과거형 사용, 대문자 누락
feat: Add Youtube Link Validation Endpoint.  # 마침표 사용, 너무 길음
```

---

## 🔄 작업 흐름 예시

다음 예시들은 이슈 템플릿을 활용한 전체 작업 흐름을 보여줍니다.

### 예시 1: 기능 개발

1. **이슈 생성**
   - GitHub에서 `New issue` → `기능 개발` 템플릿 선택
   - 제목: `[FEAT] FastAPI user input endpoint` (템플릿이 자동으로 `[FEAT]` 접두사 추가)
   - 템플릿 작성:
     - 기능 개요: "YouTube 링크를 입력받아 자막을 추출하는 FastAPI 엔드포인트 개발"
     - 목표: "사용자가 YouTube URL을 입력하면 자동으로 자막을 추출하여 단어장을 생성할 수 있도록 함"
     - 작업 내용: 체크박스로 작업 항목 나열
     - 체크리스트: 설계 → 개발 → 테스트 → 문서화 → 배포 순서로 진행 상황 체크

2. **브랜치 생성**
   - 이슈 템플릿 상단의 브랜치 가이드 참고: `feat/기능명-간단설명`
   ```bash
   git checkout -b feat/fastapi-user-input
   ```

3. **코드 작성 및 커밋**
   - 이슈 템플릿 상단의 커밋 메시지 가이드 참고
   ```bash
   git add .
   git commit -m "feat: Add user input endpoint for YouTube link"
   ```
   - 작업 진행 중 이슈의 체크리스트를 업데이트하며 진행 상황 추적

4. **PR 생성**
   - 제목: `[FEAT] FastAPI user input endpoint` (이슈 제목과 동일)
   - 또는: `feat: Add user input endpoint for YouTube link` (커밋 메시지와 동일)
   - PR 본문에 `Closes #이슈번호` 추가하여 이슈 자동 연결
   - 완료된 체크리스트 스크린샷 첨부 (선택사항)

### 예시 2: 버그 수정

1. **이슈 생성**
   - GitHub에서 `New issue` → `기능 수정` 템플릿 선택
   - 제목: `[FIX] YouTube link validation error` (템플릿이 자동으로 `[FIX]` 접두사 추가)
   - 템플릿 작성:
     - 문제 설명: "YouTube Shorts URL을 입력하면 검증 오류가 발생함"
     - 재현 방법: 단계별로 문제 재현 방법 작성
     - 예상 결과: "YouTube Shorts URL도 정상적으로 처리되어 자막이 추출됨"
     - 관련 정보: 문제 발생 파일과 라인 번호 명시

2. **브랜치 생성**
   - 이슈 템플릿 상단의 브랜치 가이드 참고: `fix/수정내용-간단설명`
   ```bash
   git checkout -b fix/youtube-link-validation-error
   ```

3. **코드 수정 및 커밋**
   - 이슈 템플릿 상단의 커밋 메시지 가이드 참고
   ```bash
   git add .
   git commit -m "fix: Correct validation logic for YouTube short URLs"
   ```
   - 체크리스트의 분석 → 수정 → 테스트 → 문서화 단계 진행

4. **PR 생성**
   - 제목: `[FIX] YouTube link validation error` (이슈 제목과 동일)
   - 또는: `fix: Correct validation logic for YouTube short URLs`
   - PR 본문에 재현 방법과 수정 내용 상세 설명
   - PR 본문에 `Closes #이슈번호` 추가

### 예시 3: 문서 작업

1. **이슈 생성**
   - GitHub에서 `New issue` → `문서 작업` 템플릿 선택
   - 제목: `[DOCS] Update installation guide` (템플릿이 자동으로 `[DOCS]` 접두사 추가)
   - 템플릿 작성:
     - 문서 개요: 작업 유형(수정), 문서명(README.md)
     - 작업 내용: 체크박스로 작업 항목 나열
     - 문서 정보: 문서 경로와 대상 섹션 명시

2. **브랜치 생성**
   - 이슈 템플릿 상단의 브랜치 가이드 참고: `docs/문서명-간단설명`
   ```bash
   git checkout -b docs/readme-installation
   ```

3. **문서 작성 및 커밋**
   - 이슈 템플릿 상단의 커밋 메시지 가이드 참고
   ```bash
   git add .
   git commit -m "docs: Update installation instructions in README"
   ```
   - 체크리스트의 준비 → 작성/수정 → 검토 → 완료 단계 진행

### 예시 4: 설정 파일 추가

1. **이슈 생성**
   - GitHub에서 `New issue` → `설정 파일 업로드` 템플릿 선택
   - 제목: `[CHORE] Add Docker Compose config` (템플릿이 자동으로 `[CHORE]` 접두사 추가)
   - 템플릿 작성:
     - 설정 파일 개요: 파일명, 작업 유형
     - 보안 확인: 민감한 정보 포함 여부 확인 (중요!)
     - 관련 파일 정보: 파일 경로와 영향 범위

2. **브랜치 생성**
   ```bash
   git checkout -b chore/docker-compose-setup
   ```

3. **설정 파일 작성 및 커밋**
   ```bash
   git add .
   git commit -m "chore: Add Docker Compose configuration for development"
   ```
   - 보안 확인 체크리스트 반드시 확인 후 커밋

---

## 📌 마무리

### 핵심 원칙

- **일관성**: 이슈, 브랜치, 커밋 메시지를 일관되게 연결하면 작업 추적이 쉬워집니다
- **타입 일치**: 각 단계에서 접두사(타입)를 일치시키세요
  - 이슈: `[FEAT]`, `[FIX]`, `[DOCS]`, `[CHORE]`
  - 브랜치: `feat/`, `fix/`, `docs/`, `chore/`
  - 커밋: `feat:`, `fix:`, `docs:`, `chore:`
- **템플릿 활용**: 불명확한 경우 이슈 템플릿의 가이드를 참고하세요
- **체크리스트**: 이슈 템플릿의 체크리스트를 활용하여 작업 진행 상황을 체계적으로 관리하세요

### 작업 흐름 요약

1. ✅ **이슈 생성**: 적절한 템플릿 선택 및 작성
2. ✅ **브랜치 생성**: 이슈 템플릿의 브랜치 가이드 참고
3. ✅ **코드 작성**: 체크리스트를 활용하여 단계별 진행
4. ✅ **커밋**: 이슈 템플릿의 커밋 메시지 가이드 참고
5. ✅ **PR 생성**: 이슈와 연결하고 완료된 체크리스트 포함

---

## 🔗 참고 자료

- [Conventional Commits](https://www.conventionalcommits.org/)
- [Git Commit Message Convention](https://gist.github.com/joshbuchea/6f47e86d2510bce28f8e7f42ae84c716)

