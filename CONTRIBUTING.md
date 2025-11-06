# 기여 가이드 (Contributing Guide)

이 문서는 프로젝트에 기여하기 위한 브랜치 네이밍, 커밋 메시지, 이슈 작성 가이드입니다.

## 📋 목차

1. [이슈 작성](#이슈-작성)
2. [브랜치 네이밍](#브랜치-네이밍)
3. [커밋 메시지](#커밋-메시지)
4. [작업 흐름 예시](#작업-흐름-예시)

---

## 🎯 이슈 작성

이슈를 생성할 때는 GitHub 이슈 템플릿을 사용하세요. 각 템플릿은 자동으로 올바른 접두사를 포함합니다.

### 이슈 접두사

| 작업 유형 | 이슈 접두사 | 예시 |
|---------|-----------|------|
| 기능 개발 | `[FEAT]` | `[FEAT] FastAPI user input endpoint` |
| 기능 수정/버그 수정 | `[FIX]` | `[FIX] YouTube link validation error` |
| 문서 작업 | `[DOCS]` | `[DOCS] Update installation guide` |
| 설정 파일 | `[CHORE]` | `[CHORE] Add Docker Compose config` |

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

### 예시 1: 기능 개발

1. **이슈 생성**
   - 제목: `[FEAT] FastAPI user input endpoint`
   - 내용: 기능 개발 이슈 템플릿 작성

2. **브랜치 생성**
   ```bash
   git checkout -b feat/fastapi-user-input
   ```

3. **코드 작성 및 커밋**
   ```bash
   git add .
   git commit -m "feat: Add user input endpoint for YouTube link"
   ```

4. **PR 생성**
   - 제목: `[FEAT] FastAPI user input endpoint`
   - 또는: `feat: Add user input endpoint for YouTube link`

### 예시 2: 버그 수정

1. **이슈 생성**
   - 제목: `[FIX] YouTube link validation error`
   - 내용: 기능 수정 이슈 템플릿 작성

2. **브랜치 생성**
   ```bash
   git checkout -b fix/youtube-link-validation-error
   ```

3. **코드 수정 및 커밋**
   ```bash
   git add .
   git commit -m "fix: Correct validation logic for YouTube short URLs"
   ```

4. **PR 생성**
   - 제목: `[FIX] YouTube link validation error`
   - 또는: `fix: Correct validation logic for YouTube short URLs`

### 예시 3: 문서 작업

1. **이슈 생성**
   - 제목: `[DOCS] Update installation guide`
   - 내용: 문서 작업 이슈 템플릿 작성

2. **브랜치 생성**
   ```bash
   git checkout -b docs/readme-installation
   ```

3. **문서 작성 및 커밋**
   ```bash
   git add .
   git commit -m "docs: Update installation instructions in README"
   ```

---

## 📌 마무리

- 이슈, 브랜치, 커밋 메시지를 일관되게 연결하면 작업 추적이 쉬워집니다
- 각 단계에서 접두사(타입)를 일치시키세요
- 불명확한 경우 이슈 템플릿의 가이드를 참고하세요

---

## 🔗 참고 자료

- [Conventional Commits](https://www.conventionalcommits.org/)
- [Git Commit Message Convention](https://gist.github.com/joshbuchea/6f47e86d2510bce28f8e7f42ae84c716)

