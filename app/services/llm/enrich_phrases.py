"""
숙어 예문 생성 모듈

LLM을 사용하여 1단계에서 추출한 숙어에 대해 예문을 생성합니다.
"""
import json
from typing import Dict, Any
from app.services.llm.client import VLLMClient
from app.services.llm.prompts import get_phrase_enrichment_prompt_v1, get_phrase_enrichment_prompt_v7
from app.core.logging import get_access_logger, get_error_logger

ACCESS_LOGGER = get_access_logger()
ERROR_LOGGER = get_error_logger()


async def enrich_phrases(
    phrase_extraction_result: Dict[str, Any],
    video_id: str
) -> Dict[str, Any]:
    """
    2단계: 1단계 숙어 추출 결과에 대해 예문을 생성합니다.
    
    Args:
        phrase_extraction_result: 1단계 숙어 추출 결과 (이미 모든 청크 병합된 결과)
            예: {
                "videoId": video_id,
                "result": {
                    "phrase1": "뜻1",
                    "phrase2": "뜻2",
                    ...
                }
            }
        video_id: 비디오 ID
        
    Returns:
        딕셔너리 형태의 결과:
        {
            "videoId": video_id,
            "result": {
                "숙어1": {
                    "예문": "Example sentence in English using the phrase."
                },
                ...
            }
        }
        
    Raises:
        ValueError: JSON 파싱 실패 또는 응답 형식 오류 시
        Exception: LLM API 호출 실패 시
    """
    # 1단계 결과에서 숙어 딕셔너리 추출
    phrases_dict = phrase_extraction_result.get("result", {})
    if not phrases_dict:
        ERROR_LOGGER.warning(f"No phrases found in extraction result - Video ID: '{video_id}'")
        return {
            "videoId": video_id,
            "result": {}
        }
    
    ACCESS_LOGGER.info(f"Start Phrase Enrichment for Video ID: '{video_id}' - Total Phrases: {len(phrases_dict)}")
    
    # 숙어와 뜻을 정규화 (뜻이 리스트인 경우 첫 번째 값 사용)
    normalized_phrases = {}
    for phrase, meaning in phrases_dict.items():
        if isinstance(meaning, str):
            normalized_phrases[phrase] = meaning
        elif isinstance(meaning, list) and len(meaning) > 0:
            normalized_phrases[phrase] = meaning[0] if isinstance(meaning[0], str) else str(meaning[0])
        else:
            normalized_phrases[phrase] = str(meaning) if meaning else ""
    
    # 재시도 로직: v1 → v7 → v1 → v7 (최대 4번 시도)
    prompt_versions = [
        ("v1", get_phrase_enrichment_prompt_v1),
        ("v7", get_phrase_enrichment_prompt_v7),
        ("v1", get_phrase_enrichment_prompt_v1),
        ("v7", get_phrase_enrichment_prompt_v7),
    ]
    
    last_error = None
    
    for attempt, (version, prompt_func) in enumerate(prompt_versions, 1):
        async with VLLMClient() as client:
            try:
                ACCESS_LOGGER.info(f"Phrase Enrichment Attempt {attempt}/4 (version: {version}) for Video ID: '{video_id}'")
                
                # 프롬프트 생성
                prompt = prompt_func(normalized_phrases, video_id)
                
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
                        f"JSON Parse Failed (Phrase Enrichment, attempt {attempt}, version {version})",
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
                        f"Invalid Response Format (Phrase Enrichment, attempt {attempt}, version {version})",
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
                
                ACCESS_LOGGER.info(f"End Phrase Enrichment for Video ID: '{video_id}' - Total Phrases: {len(result)} (Success on attempt {attempt}, version {version})")
                return final_result
                
            except Exception as e:
                from app.core.error_utils import log_error_with_location
                log_error_with_location(
                    f"Phrase Enrichment Process Failed (attempt {attempt}, version {version})",
                    f"Video ID: '{video_id}' - Error: {str(e)}",
                    error=e
                )
                last_error = e
                continue  # 다음 버전으로 재시도
    
    # 모든 시도 실패
    ERROR_LOGGER.error(f"Phrase Enrichment failed after 4 attempts for Video ID: '{video_id}'")
    raise last_error if last_error else Exception(f"Phrase Enrichment failed after 4 attempts - Video ID: '{video_id}'")

