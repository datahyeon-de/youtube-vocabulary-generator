"""
단어 추출 모듈

LLM을 사용하여 자막 청크에서 단어를 추출하고 한국어 뜻을 생성합니다.
"""
from typing import Dict, List, Any
from app.services.llm.utils import extract_from_chunks
from app.services.llm.prompts import get_word_extraction_prompt
from app.core.logging import get_access_logger

ACCESS_LOGGER = get_access_logger()


def _merge_word_results(combined_result: Dict[str, Any], chunk_result: Dict[str, Any]) -> None:
    """
    단어 추출 결과를 병합합니다.
    
    Args:
        combined_result: 누적된 결과 딕셔너리 (in-place 수정)
        chunk_result: 현재 청크의 결과 딕셔너리
    """
    # 단어들을 소문자로 정규화하여 병합
    for word, word_data in chunk_result.items():
        word_lower = word.lower().strip()
        
        # 새로운 구조: {"품사": "...", "뜻": [...]} 처리
        if isinstance(word_data, dict):
            pos = word_data.get("품사", "")
            meanings = word_data.get("뜻", [])
        # 구버전 구조 지원: ["뜻1", "뜻2"] 또는 "뜻"
        elif isinstance(word_data, list):
            pos = ""
            meanings = word_data
        elif isinstance(word_data, str):
            pos = ""
            meanings = [word_data]
        else:
            continue
        
        # 병합 로직
        if word_lower not in combined_result:
            combined_result[word_lower] = {
                "품사": pos,
                "뜻": []
            }
        else:
            # 품사가 없으면 유지, 있으면 업데이트 (나중 것 우선)
            if pos:
                combined_result[word_lower]["품사"] = pos
        
        # 뜻 추가 (중복 제거)
        if isinstance(meanings, list):
            for meaning in meanings:
                if meaning and meaning not in combined_result[word_lower]["뜻"]:
                    combined_result[word_lower]["뜻"].append(meaning)
        elif isinstance(meanings, str):
            if meanings not in combined_result[word_lower]["뜻"]:
                combined_result[word_lower]["뜻"].append(meanings)


async def extract_words_from_chunks(
    chunk_texts: List[str], 
    video_id: str
) -> Dict[str, Any]:
    """
    1단계: 청크 텍스트 리스트에서 단어를 추출하고 한국어 뜻을 생성합니다.
    
    Args:
        chunk_texts: 자막 청크 텍스트 리스트
        video_id: 비디오 ID
        
    Returns:
        딕셔너리 형태의 결과:
        {
            "videoId": video_id,
            "result": {
                "단어1": {
                    "품사": "n",
                    "뜻": ["뜻1", "뜻2"]
                },
                "단어2": {
                    "품사": "v",
                    "뜻": ["뜻1"]
                },
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
        process_name="Word Extraction",
        get_prompt_func=get_word_extraction_prompt,
        merge_results_func=_merge_word_results
    )
