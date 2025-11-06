from fastapi import APIRouter, HTTPException, status
from app.models.schemas import VideoUrlRequests, VideoUrlResponse
from app.services.validator import extract_video_id

router = APIRouter(prefix="/api/video", tags=["video"])

@router.post("/", response_model=VideoUrlResponse)
def process_video_url(request: VideoUrlRequests):
    """YouTube URL을 받아서 Video ID를 반환합니다.
    
    Args:
        request: VideoUrlRequests 스키마 (URL 포함)
        
    Returns:
        VideoUrlResponse: Video ID와 상태 정보
        
    Raises:
        HTTPException: Video ID 추출 실패 시 400 Bad Request
    """
    try:
        # Video ID 추출
        video_id = extract_video_id(request.url)
        
        # 응답 반환
        return VideoUrlResponse(
            video_id=video_id,
            status="success"
        )
    except ValueError as e:
        # 사용자 입력 오류는 400 Bad Request로 반환
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )