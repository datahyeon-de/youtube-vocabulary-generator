"""
숙어 예문 생성 모듈

LLM을 사용하여 1단계에서 추출한 숙어에 대해 예문을 생성합니다.
"""
from typing import Dict, Any
from app.services.llm.utils import enrich_with_retry
from app.services.llm.prompts import get_phrase_enrichment_prompt_v1, get_phrase_enrichment_prompt_v7


def _normalize_phrases(phrases_dict: Dict[str, Any]) -> Dict[str, str]:
    """
    숙어와 뜻을 정규화합니다 (뜻이 리스트인 경우 첫 번째 값 사용).
    
    Args:
        phrases_dict: 원본 숙어 딕셔너리
        
    Returns:
        정규화된 숙어 딕셔너리 (모든 값이 문자열)
    """
    normalized_phrases = {}
    for phrase, meaning in phrases_dict.items():
        if isinstance(meaning, str):
            normalized_phrases[phrase] = meaning
        elif isinstance(meaning, list) and len(meaning) > 0:
            normalized_phrases[phrase] = meaning[0] if isinstance(meaning[0], str) else str(meaning[0])
        else:
            normalized_phrases[phrase] = str(meaning) if meaning else ""
    return normalized_phrases


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
    # 재시도 로직: v1 → v7 (최대 2번 시도)
    prompt_versions = [
        ("v1", get_phrase_enrichment_prompt_v1),
        ("v7", get_phrase_enrichment_prompt_v7),
    ]
    
    return await enrich_with_retry(
        extraction_result=phrase_extraction_result,
        video_id=video_id,
        process_name="Phrase Enrichment",
        prompt_versions=prompt_versions,
        normalize_input=_normalize_phrases
    )
