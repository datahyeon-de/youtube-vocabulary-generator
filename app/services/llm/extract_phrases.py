"""
숙어 추출 모듈

LLM을 사용하여 자막 청크에서 숙어(idiom, phrasal verb, collocation)를 추출하고 한국어 뜻을 생성합니다.
"""
from typing import Dict, List, Any
from app.services.llm.utils import extract_from_chunks
from app.services.llm.prompts import get_phrase_extraction_prompt
from app.core.logging import get_access_logger

ACCESS_LOGGER = get_access_logger()


def _merge_phrase_results(combined_result: Dict[str, Any], chunk_result: Dict[str, Any]) -> None:
    """
    숙어 추출 결과를 병합합니다.
    
    Args:
        combined_result: 누적된 결과 딕셔너리 (in-place 수정)
        chunk_result: 현재 청크의 결과 딕셔너리
    """
    # 숙어들을 소문자로 정규화하여 병합
    for phrase, meaning in chunk_result.items():
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
    return await extract_from_chunks(
        chunk_texts=chunk_texts,
        video_id=video_id,
        process_name="Phrase Extraction",
        get_prompt_func=get_phrase_extraction_prompt,
        merge_results_func=_merge_phrase_results
    )
