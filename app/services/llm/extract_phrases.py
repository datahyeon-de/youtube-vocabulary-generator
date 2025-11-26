"""
숙어 추출 모듈

LLM을 사용하여 자막 청크에서 숙어(idiom, phrasal verb, collocation)를 추출하고 한국어 뜻을 생성합니다.
"""
import json
import asyncio
from typing import Dict, List, Any
from app.services.llm.client import VLLMClient
from app.services.llm.prompts import get_phrase_extraction_prompt
from app.core.logging import get_access_logger, get_error_logger


ACCESS_LOGGER = get_access_logger()
ERROR_LOGGER = get_error_logger()

async def _extract_phrases_from_single_chunk(
    chunk_text: str,
    chunk_idx: int,
    total_chunks: int,
    video_id: str,
    client: VLLMClient
) -> Dict[str, str]:
    """
    단일 청크에서 숙어를 추출합니다 (내부 헬퍼 함수)
    
    Args:
        chunk_text: 자막 청크 텍스트
        chunk_idx: 청크 인덱스 (1부터 시작)
        total_chunks: 전체 청크 개수
        video_id: 비디오 ID
        client: VLLMClient 인스턴스 (컨텍스트 매니저로 관리됨)
        
    Returns:
        딕셔너리 형태의 결과:
        {
            "숙어1": "뜻1",
            "숙어2": "뜻2",
            ...
        }
        
    Raises:
        ValueError: JSON 파싱 실패 또는 응답 형식 오류 시
        Exception: LLM API 호출 실패 시
    """
    try:
        # 프롬프트 생성
        prompt = get_phrase_extraction_prompt(chunk_text, video_id)
        
        # LLM API 호출
        messages = [{"role": "user", "content": prompt}]
        response = await client.chat_completion(messages, temperature=0.7)
        
        # 응답에서 콘텐츠 추출
        content = await client.extract_content_from_response(response)
        
        # 디버깅: 응답 내용 로깅 (JSON 파싱 전)
        if not content or len(content.strip()) == 0:
            from app.core.error_utils import log_error_with_location
            log_error_with_location(
                f"Empty Response for Chunk {chunk_idx}/{total_chunks}",
                f"Video ID: '{video_id}'",
                additional_info={
                    "Raw Response": str(response)[:500]
                }
            )
            raise ValueError(f"Empty Response for Chunk {chunk_idx}/{total_chunks} - Video ID: '{video_id}'")
        
        # JSON 파싱
        try:
            parsed_response = json.loads(content)
        except json.JSONDecodeError as e:
            # JSON 파싱 실패 시 실제 응답 내용과 에러 위치를 상세히 로깅
            from app.core.error_utils import log_error_with_location
            log_error_with_location(
                f"JSON Parse Failed for Chunk {chunk_idx}/{total_chunks}",
                f"Video ID: '{video_id}' - Error: {str(e)}",
                error=e,
                additional_info={
                    "Response Content (first 500 chars)": content[:500],
                    "Response Content (last 200 chars)": content[-200:] if len(content) > 500 else '',
                    "Response Length": len(content)
                }
            )
            raise ValueError(f"JSON Parse Failed for Chunk {chunk_idx}/{total_chunks} - Video ID: '{video_id}' - Error: {str(e)}") from e
        
        # 결과 검증
        result = parsed_response.get("result")
        if not result or not isinstance(result, dict):
            from app.core.error_utils import log_error_with_location
            log_error_with_location(
                f"Invalid Response Format for Chunk {chunk_idx}/{total_chunks}",
                f"Video ID: '{video_id}'",
                additional_info={
                    "Response": content[:500],
                    "Parsed Result": str(parsed_response)[:500]
                }
            )
            raise ValueError(f"Invalid Response Format for Chunk {chunk_idx}/{total_chunks} - Video ID: '{video_id}'")
        
        ACCESS_LOGGER.debug(f"Phrase Extraction Success for Chunk {chunk_idx}/{total_chunks} - Video ID: '{video_id}' - Phrases: {len(result)}")
        return result
    
    except ValueError:
        # ValueError는 이미 로깅되었으므로 재발생
        raise
        
    except Exception as e:
        # 예상치 못한 예외 발생 시 상세 정보 로깅
        from app.core.error_utils import log_error_with_location
        log_error_with_location(
            f"Phrase Extraction Failed for Chunk {chunk_idx}/{total_chunks}",
            f"Video ID: '{video_id}' - Error: {str(e)}",
            error=e
        )
        raise



async def extract_phrases_from_chunks(
    chunk_texts: List[str], 
    video_id: str
) -> Dict[str, Any]:
    """
    1단계: 청크 텍스트 리스트에서 숙어를 추출하고 한국어 뜻을 생성합니다.
    
    Args:
        chunk_texts: 자막 청크 텍스트 리스트
        video_id: 비디오 ID
        
    Returns:
        딕셔너리 형태의 결과:
        {
            "videoId": video_id,
            "result": {
                "숙어1": "뜻1",
                "숙어2": "뜻2",
                ...
            }
        }
        
    Raises:
        ValueError: JSON 파싱 실패 또는 응답 형식 오류 시
        Exception: LLM API 호출 실패 시
    """
    combined_result = {}
    
    # 숙어 추출 모듈에서 하나의 클라이언트 인스턴스 사용
    async with VLLMClient() as client:
        try:
            ACCESS_LOGGER.info(f"Start Phrase Extraction for Video ID: '{video_id}' - Total Chunks: {len(chunk_texts)}")
            
            # 모든 청크에 대해 병렬로 작업 생성 (같은 클라이언트 공유)
            tasks = [
                _extract_phrases_from_single_chunk(
                    chunk_text, idx, len(chunk_texts), video_id, client
                )
                for idx, chunk_text in enumerate(chunk_texts, start=1)
            ]
            
            # 모든 작업을 병렬로 실행 (부분 실패 허용)
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 결과 병합
            for idx, result in enumerate(results, start=1):
                if isinstance(result, Exception):
                    # 예외 발생한 청크는 로그만 남기고 건너뛰기
                    ERROR_LOGGER.error(f"Skipping Chunk {idx}/{len(chunk_texts)} due to error - Video ID: '{video_id}' - Error: {str(result)}")
                    continue
                
                if not result or not isinstance(result, dict):
                    continue
                
                # 숙어들을 소문자로 정규화하여 병합
                for phrase, meaning in result.items():
                    phrase_lower = phrase.lower().strip()
                    
                    # 뜻이 문자열인 경우 그대로 사용, 리스트인 경우 첫 번째 값 사용
                    if isinstance(meaning, str):
                        meaning_value = meaning
                    elif isinstance(meaning, list) and len(meaning) > 0:
                        meaning_value = meaning[0] if isinstance(meaning[0], str) else str(meaning[0])
                    else:
                        meaning_value = str(meaning) if meaning else ""
                    
                    # 병합 로직: 같은 숙어가 있으면 뜻을 리스트로 변환하여 중복 제거
                    if phrase_lower not in combined_result:
                        combined_result[phrase_lower] = meaning_value
                    else:
                        # 기존 뜻과 다르면 리스트로 변환하여 추가
                        existing_meaning = combined_result[phrase_lower]
                        if isinstance(existing_meaning, str):
                            if existing_meaning != meaning_value:
                                combined_result[phrase_lower] = [existing_meaning, meaning_value]
                        elif isinstance(existing_meaning, list):
                            if meaning_value not in existing_meaning:
                                combined_result[phrase_lower].append(meaning_value)
            
            # 최종 결과 구성
            final_result = {
                "videoId": video_id,
                "result": combined_result
            }
            
            ACCESS_LOGGER.info(f"End Phrase Extraction for Video ID: '{video_id}' - Total Phrases: {len(combined_result)}")
            return final_result
            
        except Exception as e:
            ERROR_LOGGER.error(f"Phrase Extraction Process Failed - Video ID: '{video_id}' - Error: {str(e)}")
            raise