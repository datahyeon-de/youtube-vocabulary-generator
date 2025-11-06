from pydantic import BaseModel, field_validator
from urllib.parse import urlparse


class VideoUrlRequests(BaseModel):
    """Video URL 요청 스키마"""
    url: str
    
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
        
        # 도메인, 경로, 쿼리 파라미터 모두 확인
        if (parsed.netloc.lower() != 'www.youtube.com' or 
            parsed.path != '/watch' or 
            'v=' not in parsed.query):
            raise ValueError(
                "YouTube URL 형식이 올바르지 않습니다. "
                "(예: https://www.youtube.com/watch?v={VIDEO_ID})"
            )
        
        return v.strip()
    
    