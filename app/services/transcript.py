from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
from typing import List
from transformers import AutoTokenizer
from app.core.config import settings
from app.core.logging import get_access_logger, get_error_logger

TOKENIZER = AutoTokenizer.from_pretrained(settings.TOKENIZER_MODEL)
MAX_TOKEN_COUNT = settings.MAX_TOKEN_COUNT
ACCESS_LOGGER = get_access_logger()
ERROR_LOGGER = get_error_logger()

def count_tokens(text: str) -> int:
    return len(TOKENIZER.encode(text))

def create_chunks(video_id: str, raw_segments: List[dict]) -> List[dict]:
    chunks = []  # 최종 청크 리스트
    current_chunk_texts = []  # 현재 청크의 텍스트들
    current_chunk_tokens = 0  # 현재 청크의 토큰 수
    chunk_start_idx = 1
    
    ACCESS_LOGGER.info(f"Start Creating Chunk for Video ID: '{video_id}'")
    for idx, segment in enumerate(raw_segments, start=1):
        segment_text = segment["text"]
        segment_tokens = count_tokens(segment_text)
        
        # 현재 청크에 추가하면 2000을 넘는지 확인
        if current_chunk_tokens + segment_tokens > MAX_TOKEN_COUNT and current_chunk_texts:
            # 현재 청크를 완성하고 저장
            chunk_text = ' '.join(current_chunk_texts)
            chunks.append({
                'text': chunk_text,
                'token_count': current_chunk_tokens,
                'segment_range': f"{chunk_start_idx}-{idx - 1}"
            })
            ACCESS_LOGGER.debug(f"Chunk Created: {len(chunks)} for Video ID: '{video_id}'")
            # 새 청크 시작
            current_chunk_texts = [segment_text]
            current_chunk_tokens = segment_tokens
            chunk_start_idx = idx
        else:
            # 현재 청크에 추가
            current_chunk_texts.append(segment_text)
            current_chunk_tokens += segment_tokens

    # 마지막 청크 추가 (남은 것이 있으면)
    if current_chunk_texts:
        chunk_text = ' '.join(current_chunk_texts)
        chunks.append({
            'text': chunk_text,
            'token_count': current_chunk_tokens,
            'segment_range': f"{chunk_start_idx}-{len(raw_segments)}"
        })
        ACCESS_LOGGER.debug(f"Chunk Created: {len(chunks)} for Video ID: '{video_id}'")
    
    ACCESS_LOGGER.info(f"End Creating Chunks for Video ID: '{video_id}'")
    ACCESS_LOGGER.info(f"Total Chunks Created: {len(chunks)} for Video ID: '{video_id}'")
    
    return chunks

def get_transcript(video_id: str) -> List[dict]:
    """YouTube 영상의 자막을 추출합니다.
    
    Args:
        video_id: YouTube 영상 ID
        
    Returns:
        List[dict]: 자막 청크 리스트. 각 청크는 다음 키를 포함합니다:
            - text: 청크 텍스트
            - token_count: 청크의 토큰 수
            - segment_range: 세그먼트 범위 (예: "1-10")
    
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
        ACCESS_LOGGER.info(f"Success To Fetch Transcript for Video ID: '{video_id}'")
        
        # FetchedTranscript 객체에서 raw_data로 변환
        raw_segments = fetched.to_raw_data()
        
        # 자막 Chunks 생성
        result = create_chunks(video_id, raw_segments)
        ACCESS_LOGGER.info(f"Success To Create Chunks for Video ID: '{video_id}'")
        return result
        
    except TranscriptsDisabled:
        msg = f"Disabled Transcripts: Video ID: '{video_id}'"
        ERROR_LOGGER.error(f"Error By {msg}")
        raise ValueError(msg)
    
    except NoTranscriptFound:
        msg = f"No Transcript Found: Video ID: '{video_id}'"
        ERROR_LOGGER.error(f"Error By {msg}")
        raise ValueError(msg)
    
    except VideoUnavailable:
        msg = f"Video Unavailable: Video ID: '{video_id}'"
        ERROR_LOGGER.error(f"Error By {msg}")
        raise ValueError(msg)
    
    except Exception as e:
        # 기타 예상치 못한 오류
        msg = f"Unexpected Error: Video ID: '{video_id}'"
        ERROR_LOGGER.error(f"Error By {msg} - {str(e)}")
        raise ValueError(msg)
        