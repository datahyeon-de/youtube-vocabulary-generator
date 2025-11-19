from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
)
from typing import Literal, Optional, List
from transformers import AutoTokenizer

TOKENIZER = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-14B-Instruct-AWQ")

def count_tokens(text: str) -> int:
    return len(TOKENIZER.encode(text))

def create_chunks(raw_segments: List[dict]) -> List[dict]:
    print("자막 청크 생성 시작")
    chunks = []  # 최종 청크 리스트
    current_chunk_texts = []  # 현재 청크의 텍스트들
    current_chunk_tokens = 0  # 현재 청크의 토큰 수

    for idx, segment in enumerate(raw_segments, start=1):
        segment_text = segment["text"]
        segment_tokens = count_tokens(segment_text)
        
        # 현재 청크에 추가하면 2000을 넘는지 확인
        if current_chunk_tokens + segment_tokens > 2000 and current_chunk_texts:
            # print(f"자막 청크 생성 중 {idx}번째 세그먼트")
            # 현재 청크를 완성하고 저장
            chunk_text = ' '.join(current_chunk_texts)
            chunks.append({
                'text': chunk_text,
                'token_count': current_chunk_tokens,
                'segment_range': f"{idx - len(current_chunk_texts)}-{idx - 1}"
            })
            
            # 새 청크 시작
            current_chunk_texts = [segment_text]
            current_chunk_tokens = segment_tokens
        else:
            # 현재 청크에 추가
            current_chunk_texts.append(segment_text)
            current_chunk_tokens += segment_tokens

    # 마지막 청크 추가 (남은 것이 있으면)
    if current_chunk_texts:
        # print(f"자막 청크 생성 완료: {len(raw_segments) - len(current_chunk_texts) + 1}-{len(raw_segments)}")
        chunk_text = ' '.join(current_chunk_texts)
        chunks.append({
            'text': chunk_text,
            'token_count': current_chunk_tokens,
            'segment_range': f"{len(raw_segments) - len(current_chunk_texts) + 1}-{len(raw_segments)}"
        })

        
    # print(f"총 청크 수: {len(chunks)}")
    
    return chunks

def get_transcript(video_id: str,) -> List[dict]:
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
        
        # FetchedTranscript 객체에서 raw_data로 변환
        raw_segments = fetched.to_raw_data()
        
        print("자막 가져오기 완료")
        
        # 자막 데이터에서 텍스트만 추출하여 하나의 문자열로 합치기
        # transcript_text = ' '.join([item['text'] for item in raw_segments])
        result = create_chunks(raw_segments)
        
        # print(result)
        
        return result
        
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
        