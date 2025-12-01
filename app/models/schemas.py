from pydantic import BaseModel, field_validator
from urllib.parse import urlparse
from typing import List


class VideoUrlRequests(BaseModel):
    """Video URL 요청 스키마"""
    url: str = "https://www.youtube.com/watch?v={VIDEO_ID}"
    
    @field_validator('url')
    @classmethod
    def validate_url_not_empty(cls, v):
        """URL이 비어있지 않은지 검증"""
        if not v or not v.strip():
            raise ValueError(
                "URL은 비어있을 수 없습니다. "
                "(예: https://www.youtube.com/watch?v={VIDEO_ID})"
            )
        return v.strip()
    
    @field_validator('url')
    @classmethod
    def validate_url_format(cls, v):
        """URL의 형식이 올바른지 검증"""
        parserd = urlparse(v.strip())
        if not parserd.scheme or not parserd.netloc:
            raise ValueError(
                "URL의 형식이 올바르지 않습니다. "
                "(예: https://www.youtube.com/watch?v={VIDEO_ID})")
        return v.strip()
    
    @field_validator('url')
    @classmethod
    def validate_youtube_url(cls, v):
        """YouTube URL 형식인지 검증 (정확히 www.youtube.com/watch?v= 형식만 허용)"""
        parsed = urlparse(v.strip())
        
        # 도메인, 경로 확인
        if (parsed.netloc.lower() != 'www.youtube.com' or 
            parsed.path != '/watch'):
            raise ValueError(
                "YouTube URL 형식이 올바르지 않습니다. "
                "(예: https://www.youtube.com/watch?v={VIDEO_ID})"
            )
        
        # v 파라미터와 값 확인
        from urllib.parse import parse_qs
        query_params = parse_qs(parsed.query)
        video_id_list = query_params.get('v')
        
        if not video_id_list or not video_id_list[0]:
            raise ValueError(
                "YouTube URL에 Video ID가 없습니다. "
                "(예: https://www.youtube.com/watch?v={VIDEO_ID})"
            )
        
        return v.strip()
    
    
class VideoUrlResponse(BaseModel):
    """YouTube URL 응답 스키마"""
    video_id: str
    status: str
    message: str | None = None
    
    
class TranscriptChunk(BaseModel):
    """Youtube 자막 Chunk 스키마"""
    text: str
    token_count: int
    segment_range: str
    
    
class TranscriptResponse(BaseModel):
    """YouTube 자막 응답 스키마"""
    video_id: str
    transcript: List[TranscriptChunk]
    status: str
    language: str = "en"
    message: str | None = None
    
    
class WordEntry(BaseModel):
    """단어 엔트리 스키마"""
    word: str
    pos: str  # 품사 (part of speech)
    meanings: List[str]  # 한국어 뜻 리스트
    synonyms: List[str]  # 동의어 리스트
    example: str  # 예문 (영어)
    
    class Config:
        json_schema_extra = {
            "example": {
                "word": "example",
                "pos": "n",
                "meanings": ["예시", "사례"],
                "synonyms": ["instance", "case"],
                "example": "This is an example sentence."
            }
        }


class PhraseEntry(BaseModel):
    """숙어 엔트리 스키마"""
    phrase: str
    meaning: str  # 한국어 뜻
    example: str  # 예문 (영어)
    
    class Config:
        json_schema_extra = {
            "example": {
                "phrase": "look forward to",
                "meaning": "기대하다",
                "example": "I look forward to meeting you."
            }
        }


class VocabularyResponse(BaseModel):
    """단어장 응답 스키마"""
    video_id: str
    words: List[WordEntry]
    phrases: List[PhraseEntry]
    status: str = "success"
    message: str | None = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "video_id": "dQw4w9WgXcQ",
                "words": [
                    {
                        "word": "example",
                        "pos": "n",
                        "meanings": ["예시", "사례"],
                        "synonyms": ["instance", "case"],
                        "example": "This is an example sentence."
                    }
                ],
                "phrases": [
                    {
                        "phrase": "look forward to",
                        "meaning": "기대하다",
                        "example": "I look forward to meeting you."
                    }
                ],
                "status": "success",
                "message": None
            }
        }
    