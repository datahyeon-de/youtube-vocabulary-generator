"""
LLM 처리 통합 모듈

전체 워크플로우를 통합하여 자막 청크에서 단어장을 생성합니다.
"""
import asyncio
from typing import Dict, Any, List
from app.services.llm.extract_words import extract_words_from_chunks
from app.services.llm.extract_phrases import extract_phrases_from_chunks
from app.services.llm.enrich_words import enrich_words
from app.services.llm.enrich_phrases import enrich_phrases
from app.services.llm.merge_results import merge_results
from app.core.logging import get_access_logger, get_error_logger

ACCESS_LOGGER = get_access_logger()
ERROR_LOGGER = get_error_logger()


async def process_vocabulary(
    chunk_texts: List[str],
    video_id: str
) -> Dict[str, Any]:
    """
    전체 워크플로우를 통합하여 자막 청크에서 단어장을 생성합니다.
    
    워크플로우:
    1. 1단계: 청크에서 단어 및 숙어 추출 (병렬 처리)
    2. 2단계: 추출된 단어 및 숙어에 대해 상세 정보 생성 (재시도 로직 포함)
    3. 3단계: 모든 결과를 병합하여 최종 단어장 형식으로 변환
    
    Args:
        chunk_texts: 자막 청크 텍스트 리스트
            예: ["chunk1 text...", "chunk2 text...", ...]
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
        
    Raises:
        ValueError: 입력 검증 실패 시
        Exception: LLM 처리 실패 시 (재시도 후에도 실패한 경우)
    """
    # 입력 검증
    if not chunk_texts or len(chunk_texts) == 0:
        ERROR_LOGGER.error(f"Empty chunk_texts for Video ID: '{video_id}'")
        raise ValueError(f"청크 텍스트가 비어있습니다. Video ID: '{video_id}'")
    
    if not video_id or not video_id.strip():
        ERROR_LOGGER.error("Empty video_id")
        raise ValueError("Video ID가 비어있습니다.")
    
    video_id = video_id.strip()
    
    ACCESS_LOGGER.info(
        f"Start Vocabulary Processing for Video ID: '{video_id}' - "
        f"Total Chunks: {len(chunk_texts)}"
    )
    
    try:
        # 1단계: 단어 및 숙어 추출 (병렬 처리)
        ACCESS_LOGGER.info(f"Stage 1: Word and Phrase Extraction for Video ID: '{video_id}'")
        
        # 단어 추출과 숙어 추출을 병렬로 실행
        word_extraction_task = extract_words_from_chunks(chunk_texts, video_id)
        phrase_extraction_task = extract_phrases_from_chunks(chunk_texts, video_id)
        
        word_extraction_result, phrase_extraction_result = await asyncio.gather(
            word_extraction_task,
            phrase_extraction_task,
            return_exceptions=True
        )
        
        # 1단계 결과 검증 및 예외 처리
        if isinstance(word_extraction_result, Exception):
            ERROR_LOGGER.error(
                f"Word Extraction Failed for Video ID: '{video_id}' - "
                f"Error: {str(word_extraction_result)}"
            )
            # 단어 추출 실패 시 빈 결과로 처리 (부분 실패 허용)
            word_extraction_result = {
                "videoId": video_id,
                "result": {}
            }
            ACCESS_LOGGER.warning(
                f"Word Extraction Failed - Using Empty Result for Video ID: '{video_id}'"
            )
        
        if isinstance(phrase_extraction_result, Exception):
            ERROR_LOGGER.error(
                f"Phrase Extraction Failed for Video ID: '{video_id}' - "
                f"Error: {str(phrase_extraction_result)}"
            )
            # 숙어 추출 실패 시 빈 결과로 처리 (부분 실패 허용)
            phrase_extraction_result = {
                "videoId": video_id,
                "result": {}
            }
            ACCESS_LOGGER.warning(
                f"Phrase Extraction Failed - Using Empty Result for Video ID: '{video_id}'"
            )
        
        # 1단계 결과가 모두 비어있는 경우 예외 발생
        words_dict = word_extraction_result.get("result", {})
        phrases_dict = phrase_extraction_result.get("result", {})
        
        if not words_dict and not phrases_dict:
            ERROR_LOGGER.error(
                f"Both Word and Phrase Extraction Failed for Video ID: '{video_id}'"
            )
            raise ValueError(
                f"단어 및 숙어 추출이 모두 실패했습니다. Video ID: '{video_id}'"
            )
        
        ACCESS_LOGGER.info(
            f"Stage 1 Complete for Video ID: '{video_id}' - "
            f"Words: {len(words_dict)}, Phrases: {len(phrases_dict)}"
        )
        
        # 2단계: 단어 및 숙어 상세 정보 생성 (재시도 로직 포함)
        ACCESS_LOGGER.info(f"Stage 2: Word and Phrase Enrichment for Video ID: '{video_id}'")
        
        # 단어 상세 정보 생성과 숙어 예문 생성을 병렬로 실행
        word_enrichment_task = enrich_words(word_extraction_result, video_id)
        phrase_enrichment_task = enrich_phrases(phrase_extraction_result, video_id)
        
        word_enrichment_result, phrase_enrichment_result = await asyncio.gather(
            word_enrichment_task,
            phrase_enrichment_task,
            return_exceptions=True
        )
        
        # 2단계 결과 검증 및 예외 처리
        if isinstance(word_enrichment_result, Exception):
            ERROR_LOGGER.error(
                f"Word Enrichment Failed for Video ID: '{video_id}' - "
                f"Error: {str(word_enrichment_result)}"
            )
            # 단어 상세 정보 생성 실패 시 빈 결과로 처리
            word_enrichment_result = {
                "videoId": video_id,
                "result": {}
            }
            ACCESS_LOGGER.warning(
                f"Word Enrichment Failed - Using Empty Result for Video ID: '{video_id}'"
            )
        
        if isinstance(phrase_enrichment_result, Exception):
            ERROR_LOGGER.error(
                f"Phrase Enrichment Failed for Video ID: '{video_id}' - "
                f"Error: {str(phrase_enrichment_result)}"
            )
            # 숙어 예문 생성 실패 시 빈 결과로 처리
            phrase_enrichment_result = {
                "videoId": video_id,
                "result": {}
            }
            ACCESS_LOGGER.warning(
                f"Phrase Enrichment Failed - Using Empty Result for Video ID: '{video_id}'"
            )
        
        ACCESS_LOGGER.info(f"Stage 2 Complete for Video ID: '{video_id}'")
        
        # 3단계: 결과 병합
        ACCESS_LOGGER.info(f"Stage 3: Merging Results for Video ID: '{video_id}'")
        
        final_result = merge_results(
            word_extraction_result,
            phrase_extraction_result,
            word_enrichment_result,
            phrase_enrichment_result,
            video_id
        )
        
        ACCESS_LOGGER.info(
            f"End Vocabulary Processing for Video ID: '{video_id}' - "
            f"Words: {len(final_result.get('words', []))}, "
            f"Phrases: {len(final_result.get('phrases', []))}"
        )
        
        return final_result
        
    except ValueError as e:
        # 입력 검증 실패는 재발생
        ERROR_LOGGER.error(
            f"Vocabulary Processing Failed (ValueError) for Video ID: '{video_id}' - "
            f"Error: {str(e)}"
        )
        raise
    
    except Exception as e:
        # 예상치 못한 예외 발생 시 상세 정보 로깅
        ERROR_LOGGER.error(
            f"Vocabulary Processing Failed (Unexpected Error) for Video ID: '{video_id}' - "
            f"Error: {str(e)}",
            exc_info=True
        )
        raise Exception(
            f"단어장 생성 중 오류가 발생했습니다. Video ID: '{video_id}' - Error: {str(e)}"
        ) from e