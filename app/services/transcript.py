from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
)

from typing import Literal, Optional, List

def get_transcript(video_id: str,) -> str:
    """YouTube 영상의 자막을 추출합니다.
    
    Args:
        video_id: YouTube 영상 ID
        
    Returns:
        str: 자막 텍스트
    
    Raises:
        ValueError: 자막 추출 실패 시
            - 자막이 없는 영상: NoTranscriptFound
            - 존재하지 않는 영상: VideoUnavailable
            - 자막이 비활성화된 영상: TranscriptsDisabled
    """
    try:
        # YouTubeTranscriptApi 인스턴스 생성
        api = YouTubeTranscriptApi()
        
        # 자막 가져오기 (영어 우선, 없으면 다른 언어)
        fetched = api.fetch(video_id, languages=["en"])
        
        # FetchedTranscript 객체에서 raw_data로 변환
        raw_segments = fetched.to_raw_data()
        
        # 자막 데이터에서 텍스트만 추출하여 하나의 문자열로 합치기
        transcript_text = ' '.join([item['text'] for item in raw_segments])
        
        return transcript_text
        
    except TranscriptsDisabled:
        raise ValueError(
            f"Video ID '{video_id}'의 영상은 자막이 비활성화되어 있습니다."
        )
    except NoTranscriptFound:
        raise ValueError(
            f"Video ID '{video_id}'의 영상에는 자막이 없습니다."
        )
    except VideoUnavailable:
        raise ValueError(
            f"Video ID '{video_id}'의 영상을 찾을 수 없거나 비공개입니다."
        )
    except Exception as e:
        # 기타 예상치 못한 오류
        raise ValueError(
            f"자막을 추출하는 중 오류가 발생했습니다: {str(e)}"
        )
        