"""
LLM 서비스 공통 유틸리티 모듈

재시도 로직, 청크 처리 로직 등 공통 기능을 제공합니다.
"""
import json
import asyncio
from typing import Dict, List, Any, Callable
from app.services.llm.client import VLLMClient
from app.core.logging import get_access_logger, get_error_logger
from app.core.error_utils import log_error_with_location

ACCESS_LOGGER = get_access_logger()
ERROR_LOGGER = get_error_logger()


async def enrich_with_retry(
    extraction_result: Dict[str, Any],
    video_id: str,
    process_name: str,
    prompt_versions: List[tuple],
    normalize_input: Callable[[Dict[str, Any]], Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    상세화(enrichment) 작업을 재시도 로직과 함께 수행하는 고차 함수.
    
    Args:
        extraction_result: 1단계 추출 결과 (이미 모든 청크 병합된 결과)
        video_id: 비디오 ID
        process_name: 프로세스 이름 (예: "Word Enrichment", "Phrase Enrichment")
        prompt_versions: 프롬프트 버전 리스트 [(version, prompt_func), ...]
        normalize_input: 입력 데이터 정규화 함수 (선택적)
        
    Returns:
        딕셔너리 형태의 결과:
        {
            "videoId": video_id,
            "result": {...}
        }
        
    Raises:
        ValueError: JSON 파싱 실패 또는 응답 형식 오류 시
        Exception: LLM API 호출 실패 시
    """
    # 1단계 결과에서 딕셔너리 추출
    result_dict = extraction_result.get("result", {})
    if not result_dict:
        ERROR_LOGGER.warning(f"No items found in extraction result - Video ID: '{video_id}'")
        return {
            "videoId": video_id,
            "result": {}
        }
    
    # 입력 정규화 (선택적)
    if normalize_input:
        result_dict = normalize_input(result_dict)
    
    ACCESS_LOGGER.info(f"Start {process_name} for Video ID: '{video_id}' - Total Items: {len(result_dict)}")
    
    last_error = None
    
    for attempt, (version, prompt_func) in enumerate(prompt_versions, 1):
        async with VLLMClient() as client:
            try:
                ACCESS_LOGGER.info(f"{process_name} Attempt {attempt}/{len(prompt_versions)} (version: {version}) for Video ID: '{video_id}'")
                
                # 프롬프트 생성
                prompt = prompt_func(result_dict, video_id)
                
                # LLM API 호출
                messages = [{"role": "user", "content": prompt}]
                response = await client.chat_completion(messages, temperature=0.7)
                
                # 응답에서 콘텐츠 추출
                content = await client.extract_content_from_response(response)
                
                # JSON 파싱
                try:
                    parsed_result = json.loads(content)
                except json.JSONDecodeError as e:
                    log_error_with_location(
                        f"JSON Parse Failed ({process_name}, attempt {attempt}, version {version})",
                        f"Video ID: '{video_id}' - Error: {str(e)}",
                        error=e,
                        additional_info={
                            "Response Content (first 500 chars)": content[:500],
                            "Response Content (last 200 chars)": content[-200:] if len(content) > 500 else '',
                            "Response Length": len(content)
                        }
                    )
                    last_error = ValueError(f"JSON Parse Failed - Video ID: '{video_id}' - Error: {str(e)}")
                    continue  # 다음 버전으로 재시도
                
                # 결과 검증
                result = parsed_result.get("result")
                if not result or not isinstance(result, dict):
                    log_error_with_location(
                        f"Invalid Response Format ({process_name}, attempt {attempt}, version {version})",
                        f"Video ID: '{video_id}'",
                        additional_info={
                            "Response": content[:500],
                            "Parsed Result": str(parsed_result)[:500]
                        }
                    )
                    last_error = ValueError(f"Invalid Response Format - Video ID: '{video_id}'")
                    continue  # 다음 버전으로 재시도
                
                # 성공: 최종 결과 구성
                final_result = {
                    "videoId": video_id,
                    "result": result
                }
                
                ACCESS_LOGGER.info(f"End {process_name} for Video ID: '{video_id}' - Total Items: {len(result)} (Success on attempt {attempt}, version {version})")
                return final_result
                
            except Exception as e:
                log_error_with_location(
                    f"{process_name} Process Failed (attempt {attempt}, version {version})",
                    f"Video ID: '{video_id}' - Error: {str(e)}",
                    error=e
                )
                last_error = e
                continue  # 다음 버전으로 재시도
    
    # 모든 시도 실패
    ERROR_LOGGER.error(f"{process_name} failed after {len(prompt_versions)} attempts for Video ID: '{video_id}'")
    raise last_error if last_error else Exception(f"{process_name} failed after {len(prompt_versions)} attempts - Video ID: '{video_id}'")


async def extract_from_chunks(
    chunk_texts: List[str],
    video_id: str,
    process_name: str,
    get_prompt_func: Callable[[str, str], str],
    merge_results_func: Callable[[Dict[str, Any], Dict[str, Any]], None]
) -> Dict[str, Any]:
    """
    청크 리스트에서 추출 작업을 병렬로 수행하는 제네릭 함수.
    
    Args:
        chunk_texts: 자막 청크 텍스트 리스트
        video_id: 비디오 ID
        process_name: 프로세스 이름 (예: "Word Extraction", "Phrase Extraction")
        get_prompt_func: 프롬프트 생성 함수 (chunk_text, video_id) -> str
        merge_results_func: 결과 병합 함수 (combined_result, chunk_result) -> None
        
    Returns:
        딕셔너리 형태의 결과:
        {
            "videoId": video_id,
            "result": {...}
        }
        
    Raises:
        ValueError: JSON 파싱 실패 또는 응답 형식 오류 시
        Exception: LLM API 호출 실패 시
    """
    async def _extract_from_single_chunk(
        chunk_text: str,
        chunk_idx: int,
        total_chunks: int,
        video_id: str,
        client: VLLMClient
    ) -> Dict[str, Any]:
        """단일 청크에서 추출 작업 수행"""
        try:
            # 프롬프트 생성
            prompt = get_prompt_func(chunk_text, video_id)
            
            # LLM API 호출
            messages = [{"role": "user", "content": prompt}]
            response = await client.chat_completion(messages, temperature=0.7)
            
            # 응답에서 콘텐츠 추출
            content = await client.extract_content_from_response(response)
            
            # 디버깅: 응답 내용 로깅 (JSON 파싱 전)
            if not content or len(content.strip()) == 0:
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
                parsed_result = json.loads(content)
            except json.JSONDecodeError as e:
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
            result = parsed_result.get("result")
            if not result or not isinstance(result, dict):
                log_error_with_location(
                    f"Invalid Response Format for Chunk {chunk_idx}/{total_chunks}",
                    f"Video ID: '{video_id}'",
                    additional_info={
                        "Response": content[:500],
                        "Parsed Result": str(parsed_result)[:500]
                    }
                )
                raise ValueError(f"Invalid Response Format for Chunk {chunk_idx}/{total_chunks} - Video ID: '{video_id}'")
            
            ACCESS_LOGGER.debug(f"{process_name} Success for Chunk {chunk_idx}/{total_chunks} - Video ID: '{video_id}' - Items: {len(result)}")
            return result
            
        except ValueError:
            # ValueError는 이미 로깅되었으므로 재발생
            raise
            
        except Exception as e:
            # 예상치 못한 예외 발생 시 상세 정보 로깅
            log_error_with_location(
                f"{process_name} Failed for Chunk {chunk_idx}/{total_chunks}",
                f"Video ID: '{video_id}' - Error: {str(e)}",
                error=e
            )
            raise
    
    combined_result = {}
    
    # 하나의 클라이언트 인스턴스 사용
    async with VLLMClient() as client:
        try:
            ACCESS_LOGGER.info(f"Start {process_name} for Video ID: '{video_id}' - Total Chunks: {len(chunk_texts)}")
            
            # 모든 청크에 대해 병렬로 작업 생성 (같은 클라이언트 공유)
            tasks = [
                _extract_from_single_chunk(
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
                
                # 병합 로직 적용
                merge_results_func(combined_result, result)
            
            # 최종 결과 구성
            final_result = {
                "videoId": video_id,
                "result": combined_result
            }
            
            ACCESS_LOGGER.info(f"End {process_name} for Video ID: '{video_id}' - Total Items: {len(combined_result)}")
            return final_result
            
        except Exception as e:
            ERROR_LOGGER.error(f"{process_name} Process Failed - Video ID: '{video_id}' - Error: {str(e)}")
            raise

