# youtube-transcript-api 정리

## 1. 기본 정보
- 패키지명: `youtube-transcript-api`
- 버전: 1.2.3
- 공식 문서: https://github.com/jdepoix/youtube-transcript-api

## 2. 설치
```bash
pip install youtube-transcript-api==1.2.3
```

## 3. 기본 사용법

### 3.1 인스턴스 생성
```python
from youtube_transcript_api import YouTubeTranscriptApi

api = YouTubeTranscriptApi()
```
- `YouTubeTranscriptApi`는 내부적으로 `requests.Session`을 사용하므로 쓰레드마다 별도 인스턴스를 쓰는 것이 권장됩니다.

### 3.2 자막 목록 조회
```python
transcript_list = api.list("VIDEO_ID")
```
- `TranscriptList` 객체를 반환합니다.
- 반복문으로 순회하면 `Transcript` 객체를 하나씩 얻을 수 있습니다.

```python
for transcript in transcript_list:
    print(transcript.video_id)
    print(transcript.language, transcript.language_code)
    print(transcript.is_generated)
    print(transcript.is_translatable)
    print(transcript.translation_languages)
```

### 3.3 특정 언어 자막 선택 후 가져오기
```python
transcript = transcript_list.find_transcript(["en", "ko"])
fetched = transcript.fetch()
```
- `find_transcript`는 언어 우선순위를 배열로 받습니다.
- `fetch()`는 `FetchedTranscript` 객체를 반환합니다.

### 3.4 단축 함수 `fetch`
```python
fetched = api.fetch("VIDEO_ID", languages=["en"])
```
- `list().find_transcript().fetch()`를 한 번에 처리하는 헬퍼입니다.
- `FetchedTranscript`를 바로 돌려줍니다.

### 3.5 자막 데이터 활용
```python
first_snippet = fetched[0]
print(first_snippet.text, first_snippet.start, first_snippet.duration)

raw_segments = fetched.to_raw_data()
print(raw_segments[:2])
```
- `FetchedTranscript`는 iterable이라 `for snippet in fetched:`로 순회 가능합니다.
- `to_raw_data()`는 `[{text, start, duration}, ...]` 형태 리스트를 돌려줍니다.

## 4. Video ID로 얻을 수 있는 정보

| 항목 | 설명 | 제공 위치 |
|------|------|-----------|
| `video_id` | 조회한 유튜브 영상 ID | `Transcript`, `FetchedTranscript` |
| `language`, `language_code` | 자막 언어 이름과 코드 | `Transcript`, `FetchedTranscript` |
| `is_generated` | 자동 생성 자막 여부 | `Transcript`, `FetchedTranscript` |
| `is_translatable` | 번역 가능한 자막인지 표시 | `Transcript` |
| `translation_languages` | 번역 가능한 언어 목록 | `Transcript` |
| `snippets` | 자막 조각 리스트 | `FetchedTranscript` |
| `text` | 자막 문자열 (각 snippet) | `FetchedTranscriptSnippet` |
| `start` | 자막 시작 시간(초) | `FetchedTranscriptSnippet` |
| `duration` | 자막 표시 시간(초) | `FetchedTranscriptSnippet` |

- 제목, 설명 등 메타데이터는 이 패키지에서 제공하지 않습니다.
- 번역이 가능한 경우 `transcript.translate('ko').fetch()` 형태로 다른 언어 자막을 얻을 수 있습니다.

## 5. 대표 예외
- `NoTranscriptFound`: 요청한 언어 자막이 없을 때
- `TranscriptsDisabled`: 업로더가 자막 기능을 꺼둔 경우
- `VideoUnavailable`: 비공개·삭제 등으로 접근 불가
- `TooManyRequests`: 과도한 요청으로 제한
- (추가 예외는 `_errors` 모듈 참고)

```python
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound

api = YouTubeTranscriptApi()

try:
    fetched = api.fetch("VIDEO_ID", languages=["en"])
except NoTranscriptFound:
    print("요청 언어 자막 없음")
```

## 6. 참고 자료
- GitHub README (OST–) 링크
- 패키지 사용 중 발견한 팁이나 주의사항을 여기에 계속 추가

## 7. 내부 동작과 주의사항

- 이 패키지는 유튜브 공식 Data API 대신, 웹 페이지에서 사용하는 **내부(InnerTube) API**를 직접 호출한다.
  - `_settings.py`에서 확인할 수 있는 `WATCH_URL` → `INNERTUBE_API_URL` 흐름으로 자막 JSON을 얻는다.
  - HTML을 파싱하여 자막 URL·언어 목록을 찾고, 이후 `https://www.youtube.com/youtubei/v1/get_transcript`에 POST 요청을 보내 자막 데이터를 받아온다.
- 비공식 API를 흉내 내는 방식이므로 YouTube 측 변경에 취약하다.
  - 구조가 바뀌거나 보안 정책이 강화되면 즉시 동작이 깨질 수 있다.
  - 잦은 호출 시 429, `IpBlocked`, `RequestBlocked` 등의 예외가 발생할 수 있으며 CAPTCHA가 요구될 가능성도 있다.
- 서비스에 도입할 경우 법적·정책적 리스크를 검토해야 하고, 장애나 API 변경에 대비한 우회/대체 방안을 마련할 필요가 있다.

## 8. 공식·안정적인 자막 수집 방법

1. **YouTube Data API v3 – Captions 리소스**
   - `videos.list`로 자막이 존재하는지 확인 후, `captions.list`로 트랙 ID를 가져옴.
   - `captions.download` 엔드포인트로 실제 자막 파일을 다운로드할 수 있다.
   - 전제 조건: API 키 + OAuth 2.0 인증(영상 업로드한 계정 권한 또는 공개 자막 접근 권한) 필요.
   - 다운로드 포맷은 `.srt`, `.ttml`, `.vtt` 등으로 받을 수 있고, 공식 API이므로 안정성이 높다.
   - 단점: 사용자 인증·권한이 필요해 구현이 복잡하며, 비공개 영상이나 자막 권한이 제한된 경우 접근이 불가능하다.

2. **YouTube Player API(iframe) + 공식 CC 트랙**
   - 플레이어에서 노출되는 CC 자막을 파싱하는 방식은 여전히 비공식 처리라 안정성이 떨어진다.
   - youtube-transcript-api와 유사한 원리이므로 “공식”이라 보긴 어렵다.

3. **직접 다운로드(사용자 제공)**
   - 사용자가 `.srt`/`.vtt` 자막 파일을 직접 업로드하는 방법.
   - 기술적 의존성이 없고 가장 안전하지만, 자동화 측면에서는 불편하다.

> 프로젝트의 안정성을 중시한다면 **YouTube Data API의 captions.download**를 검토하는 것이 가장 공식적이고 장기적으로 유지보수가 쉽다. 다만 인증 과정과 권한 관리가 필요하며, 사용자가 업로드하지 않은 영상의 자막을 가져오기는 어렵다.
