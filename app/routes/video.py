from fastapi import APIRouter, HTTPException, status
from app.models.schemas import VideoUrlRequests, VideoUrlResponse, TranscriptResponse
from app.services.validator import extract_video_id
from app.services.transcript import get_transcript

router = APIRouter(prefix="/api/video", tags=["video"])

@router.post("/", response_model=VideoUrlResponse)
def post_process_video_url(request: VideoUrlRequests):
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
        

@router.post("/{video_id}/transcript", response_model=TranscriptResponse)
def post_get_video_transcript(video_id: str):
    """YouTube 영상의 자막을 추출합니다.
    
    Args:
        video_id: YouTube 영상 ID
        
    Returns:
        TranscriptResponse: 자막 텍스트와 상태 정보
    """
    try:
        # 자막 추출
        transcript_list = get_transcript(video_id)
        
        # 응답 반환
        return TranscriptResponse(
            video_id=video_id,
            transcript=transcript_list,
            status="success",
            language="en",
            message=None
        )
    except ValueError as e:
        # 사용자 입력 오류는 400 Bad Request로 반환
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


