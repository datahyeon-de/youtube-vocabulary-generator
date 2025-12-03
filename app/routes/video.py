from fastapi import APIRouter, HTTPException, status
from pydantic import ValidationError
from app.models.schemas import (
    VideoUrlRequests, 
    VideoUrlResponse, 
    TranscriptResponse,
    VocabularyResponse,
    WordEntry,
    PhraseEntry
)
from app.services.validator import extract_video_id
from app.services.transcript import get_transcript
from app.services.llm.processor import process_vocabulary
from app.core.logging import get_error_logger

router = APIRouter(prefix="/api/video", tags=["video"])
ERROR_LOGGER = get_error_logger()

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
        # Video ID 추출 실패
        # 실제 에러는 로그에 기록하고, 사용자에게는 일반적인 메시지 제공
        ERROR_LOGGER.error(
            f"Video ID extraction failed - URL: '{request.url}' - Error: {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="올바른 YouTube URL 형식이 아닙니다. (예: https://www.youtube.com/watch?v=VIDEO_ID)"
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
        # 자막 추출 실패
        # 실제 에러는 로그에 기록하고, 사용자에게는 일반적인 메시지 제공
        ERROR_LOGGER.error(
            f"Transcript extraction failed for Video ID: '{video_id}' - Error: {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="자막을 추출할 수 없습니다. 자막이 활성화되어 있고 공개된 영상인지 확인해주세요."
        )


@router.post("/{video_id}/vocabulary", response_model=VocabularyResponse)
async def post_generate_vocabulary(video_id: str):
    """YouTube 영상의 자막을 기반으로 단어장을 생성합니다.
    
    Args:
        video_id: YouTube 영상 ID
        
    Returns:
        VocabularyResponse: 단어장 정보 (단어 및 숙어 리스트)
        
    Raises:
        HTTPException: 
            - 자막 추출 실패 시 400 Bad Request
            - LLM 처리 실패 시 500 Internal Server Error
    """
    try:
        # 1. 자막 추출
        transcript_list = get_transcript(video_id)
        
        # 2. 청크 텍스트 리스트 추출
        chunk_texts = [chunk.get("text", "") for chunk in transcript_list]
        
        if not chunk_texts:
            ERROR_LOGGER.warning(
                f"Empty transcript chunks for Video ID: '{video_id}'"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="자막이 비어있습니다. 자막이 있는 영상인지 확인해주세요."
            )
        
        # 3. LLM 처리 (비동기)
        result = await process_vocabulary(chunk_texts, video_id)
        
        # 4. 딕셔너리를 Pydantic 모델로 변환
        # processor.py는 camelCase를 사용하지만, 스키마는 snake_case를 사용
        words = []
        for word_data in result.get("words", []):
            try:
                words.append(WordEntry(**word_data))
            except ValidationError as e:
                # Pydantic ValidationError만 명시적으로 처리
                # 개별 단어 변환 실패 시 로그만 남기고 건너뛰기
                ERROR_LOGGER.warning(
                    f"Skipping word entry due to validation error - "
                    f"Video ID: '{video_id}' - Word: {word_data.get('word', 'unknown')} - Error: {str(e)}"
                )
                continue
        
        phrases = []
        for phrase_data in result.get("phrases", []):
            try:
                phrases.append(PhraseEntry(**phrase_data))
            except ValidationError as e:
                # Pydantic ValidationError만 명시적으로 처리
                # 개별 숙어 변환 실패 시 로그만 남기고 건너뛰기
                ERROR_LOGGER.warning(
                    f"Skipping phrase entry due to validation error - "
                    f"Video ID: '{video_id}' - Phrase: {phrase_data.get('phrase', 'unknown')} - Error: {str(e)}"
                )
                continue
        
        # 5. 응답 반환
        return VocabularyResponse(
            video_id=result.get("videoId", video_id),
            words=words,
            phrases=phrases,
            status="success",
            message=None
        )
        
    except ValueError as e:
        # 자막 추출 실패 또는 LLM 처리 실패 등 (사용자 입력 오류 또는 처리 오류)
        # 실제 에러는 로그에 기록하고, 사용자에게는 일반적인 메시지 제공
        ERROR_LOGGER.error(
            f"Vocabulary generation failed for Video ID: '{video_id}' - Error: {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="단어장 생성 중 오류가 발생했습니다. 입력값을 확인하거나 잠시 후 다시 시도해주세요."
        )
    except HTTPException:
        # 이미 HTTPException이 발생한 경우 재발생
        raise
    except Exception as e:
        # LLM 처리 실패 등 (서버 내부 오류)
        # 실제 에러는 로그에 기록하고, 사용자에게는 일반적인 메시지 제공
        ERROR_LOGGER.error(
            f"Vocabulary generation failed for Video ID: '{video_id}' - Error: {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="일시적인 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
        )


