"""
결과 병합 모듈

1단계와 2단계의 결과를 병합하여 최종 단어장 형식으로 변환합니다.
"""
from typing import Dict, Any, List
from app.core.logging import get_access_logger, get_error_logger

ACCESS_LOGGER = get_access_logger()
ERROR_LOGGER = get_error_logger()


def merge_results(
    word_extraction_result: Dict[str, Any],
    phrase_extraction_result: Dict[str, Any],
    word_enrichment_result: Dict[str, Any],
    phrase_enrichment_result: Dict[str, Any],
    video_id: str
) -> Dict[str, Any]:
    """
    3단계: 1단계와 2단계의 결과를 병합하여 최종 단어장 형식으로 변환합니다.
    
    Args:
        word_extraction_result: 1단계 단어 추출 결과
            예: {
                "videoId": video_id,
                "result": {
                    "word1": {"품사": "n", "뜻": ["뜻1", "뜻2"]},
                    "word2": {"품사": "v", "뜻": ["뜻1"]},
                    ...
                }
            }
        phrase_extraction_result: 1단계 숙어 추출 결과
            예: {
                "videoId": video_id,
                "result": {
                    "phrase1": "뜻1",
                    "phrase2": "뜻2",
                    ...
                }
            }
        word_enrichment_result: 2단계 단어 상세 정보 결과
            예: {
                "videoId": video_id,
                "result": {
                    "word1": {
                        "동의어": ["synonym1", "synonym2"],
                        "예문": "Example sentence in English."
                    },
                    ...
                }
            }
        phrase_enrichment_result: 2단계 숙어 예문 결과
            예: {
                "videoId": video_id,
                "result": {
                    "phrase1": {
                        "예문": "Example sentence in English using the phrase."
                    },
                    ...
                }
            }
        video_id: 비디오 ID
        
    Returns:
        최종 단어장 형식의 딕셔너리:
        {
            "videoId": video_id,
            "words": [
                {
                    "word": "word1",
                    "pos": "n",
                    "meanings": ["뜻1", "뜻2"],
                    "synonyms": ["synonym1", "synonym2"],
                    "example": "Example sentence in English."
                },
                ...
            ],
            "phrases": [
                {
                    "phrase": "phrase1",
                    "meaning": "뜻1",
                    "example": "Example sentence in English using the phrase."
                },
                ...
            ]
        }
    """
    ACCESS_LOGGER.info(f"Start Merging Results for Video ID: '{video_id}'")
    
    # 1단계 결과 추출
    words_dict = word_extraction_result.get("result", {})
    phrases_dict = phrase_extraction_result.get("result", {})
    
    # 2단계 결과 추출
    word_enrichment_dict = word_enrichment_result.get("result", {})
    phrase_enrichment_dict = phrase_enrichment_result.get("result", {})
    
    # 단어 병합
    words_list = []
    for word_key, word_data in words_dict.items():
        # word_key는 소문자로 정규화되어 있음
        word = word_key
        
        # 1단계 데이터 추출
        pos = word_data.get("품사", "")
        meanings = word_data.get("뜻", [])
        
        # meanings가 리스트가 아닌 경우 리스트로 변환
        if not isinstance(meanings, list):
            meanings = [meanings] if meanings else []
        
        # 2단계 데이터 추출 (소문자 키로 조회)
        enrichment_data = word_enrichment_dict.get(word_key, {})
        synonyms = enrichment_data.get("동의어", [])
        example = enrichment_data.get("예문", "")
        
        # synonyms가 리스트가 아닌 경우 리스트로 변환
        if not isinstance(synonyms, list):
            synonyms = [synonyms] if synonyms else []
        
        # 단어 엔트리 생성
        word_entry = {
            "word": word,
            "pos": pos,
            "meanings": meanings,
            "synonyms": synonyms,
            "example": example
        }
        
        words_list.append(word_entry)
    
    # 숙어 병합
    phrases_list = []
    for phrase_key, meaning in phrases_dict.items():
        # phrase_key는 소문자로 정규화되어 있음
        phrase = phrase_key
        
        # meaning이 리스트인 경우 첫 번째 값 사용
        if isinstance(meaning, list):
            meaning_value = meaning[0] if len(meaning) > 0 else ""
        else:
            meaning_value = str(meaning) if meaning else ""
        
        # 2단계 데이터 추출 (소문자 키로 조회)
        enrichment_data = phrase_enrichment_dict.get(phrase_key, {})
        example = enrichment_data.get("예문", "")
        
        # 숙어 엔트리 생성
        phrase_entry = {
            "phrase": phrase,
            "meaning": meaning_value,
            "example": example
        }
        
        phrases_list.append(phrase_entry)
    
    # 최종 결과 구성
    final_result = {
        "videoId": video_id,
        "words": words_list,
        "phrases": phrases_list
    }
    
    ACCESS_LOGGER.info(
        f"End Merging Results for Video ID: '{video_id}' - "
        f"Words: {len(words_list)}, Phrases: {len(phrases_list)}"
    )
    
    return final_result