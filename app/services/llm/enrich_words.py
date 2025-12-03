"""
단어 상세 정보 생성 모듈

LLM을 사용하여 1단계에서 추출한 단어에 대해 동의어와 예문을 생성합니다.
"""
from typing import Dict, Any
from app.services.llm.utils import enrich_with_retry
from app.services.llm.prompts import get_word_enrichment_prompt_v1, get_word_enrichment_prompt_v7


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
    # 재시도 로직: v1 → v7 (최대 2번 시도)
    prompt_versions = [
        ("v1", get_word_enrichment_prompt_v1),
        ("v7", get_word_enrichment_prompt_v7),
    ]
    
    return await enrich_with_retry(
        extraction_result=word_extraction_result,
        video_id=video_id,
        process_name="Word Enrichment",
        prompt_versions=prompt_versions
    )
