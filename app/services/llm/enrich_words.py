"""
단어 상세 정보 생성 모듈

LLM을 사용하여 1단계에서 추출한 단어에 대해 동의어와 예문을 생성합니다.
"""
import json
from typing import Dict, Any
from app.services.llm.client import VLLMClient
from app.services.llm.prompts import get_word_enrichment_prompt_v1, get_word_enrichment_prompt_v7
from app.core.logging import get_access_logger, get_error_logger

ACCESS_LOGGER = get_access_logger()
ERROR_LOGGER = get_error_logger()


async def enrich_words(
    word_extraction_result: Dict[str, Any],
    video_id: str
) -> Dict[str, Any]:
    """
    2단계: 1단계 단어 추출 결과에 대해 동의어와 예문을 생성합니다.
    
    Args:
        word_extraction_result: 1단계 단어 추출 결과 (이미 모든 청크 병합된 결과)
            예: {
                "videoId": video_id,
                "result": {
                    "word1": {"품사": "n", "뜻": ["뜻1", "뜻2"]},
                    "word2": {"품사": "v", "뜻": ["뜻1"]},
                    ...
                }
            }
        video_id: 비디오 ID
        
    Returns:
        딕셔너리 형태의 결과:
        {
            "videoId": video_id,
            "result": {
            "단어1": {
                "동의어": ["synonym1", "synonym2"],
                "예문": "Example sentence in English."
            },
            ...
            }
        }
        
    Raises:
        ValueError: JSON 파싱 실패 또는 응답 형식 오류 시
        Exception: LLM API 호출 실패 시
    """
    # 1단계 결과에서 단어 딕셔너리 추출
    words_dict = word_extraction_result.get("result", {})
    if not words_dict:
        ERROR_LOGGER.warning(f"No words found in extraction result - Video ID: '{video_id}'")
        return {
            "videoId": video_id,
            "result": {}
        }
    
    ACCESS_LOGGER.info(f"Start Word Enrichment for Video ID: '{video_id}' - Total Words: {len(words_dict)}")
    
    # 재시도 로직: v1 → v7 → v1 → v7 (최대 4번 시도)
    prompt_versions = [
        ("v1", get_word_enrichment_prompt_v1),
        ("v7", get_word_enrichment_prompt_v7),
        ("v1", get_word_enrichment_prompt_v1),
        ("v7", get_word_enrichment_prompt_v7),
    ]
    
    last_error = None
    
    for attempt, (version, prompt_func) in enumerate(prompt_versions, 1):
        async with VLLMClient() as client:
            try:
                ACCESS_LOGGER.info(f"Word Enrichment Attempt {attempt}/4 (version: {version}) for Video ID: '{video_id}'")
                
                # 프롬프트 생성
                prompt = prompt_func(words_dict, video_id)
                
                # LLM API 호출
                messages = [{"role": "user", "content": prompt}]
                response = await client.chat_completion(messages, temperature=0.7)
                
                # 응답에서 콘텐츠 추출
                content = await client.extract_content_from_response(response)
                
                # JSON 파싱
                try:
                    parsed_result = json.loads(content)
                except json.JSONDecodeError as e:
                    from app.core.error_utils import log_error_with_location
                    log_error_with_location(
                        f"JSON Parse Failed (Word Enrichment, attempt {attempt}, version {version})",
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
                    from app.core.error_utils import log_error_with_location
                    log_error_with_location(
                        f"Invalid Response Format (Word Enrichment, attempt {attempt}, version {version})",
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
                
                ACCESS_LOGGER.info(f"End Word Enrichment for Video ID: '{video_id}' - Total Words: {len(result)} (Success on attempt {attempt}, version {version})")
                return final_result
                
            except Exception as e:
                from app.core.error_utils import log_error_with_location
                log_error_with_location(
                    f"Word Enrichment Process Failed (attempt {attempt}, version {version})",
                    f"Video ID: '{video_id}' - Error: {str(e)}",
                    error=e
                )
                last_error = e
                continue  # 다음 버전으로 재시도
    
    # 모든 시도 실패
    ERROR_LOGGER.error(f"Word Enrichment failed after 4 attempts for Video ID: '{video_id}'")
    raise last_error if last_error else Exception(f"Word Enrichment failed after 4 attempts - Video ID: '{video_id}'")
