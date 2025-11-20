"""
단어 추출 모듈

LLM을 사용하여 자막 청크에서 단어를 추출하고 한국어 뜻을 생성합니다.
"""
import json
from typing import Dict, List, Any
from app.services.llm.client import get_vllm_client
from app.services.llm.prompts import get_word_extraction_prompt
from app.core.logging import get_access_logger, get_error_logger

ACCESS_LOGGER = get_access_logger()
ERROR_LOGGER = get_error_logger()


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
                "단어1": ["뜻1", "뜻2"],
                "단어2": ["뜻1"],
                ...
            }
        }
        
    Raises:
        ValueError: JSON 파싱 실패 또는 응답 형식 오류 시
        Exception: LLM API 호출 실패 시
    """
    client = await get_vllm_client()
    combined_result = {}
    
    try:
        ACCESS_LOGGER.info(f"Start Word Extraction for Video ID: '{video_id}' - Total Chunks: {len(chunk_texts)}")
        
        # 각 청크에 대해 단어 추출 수행
        for idx, chunk_text in enumerate(chunk_texts, start=1):
            try:
                # 프롬프트 생성
                prompt = get_word_extraction_prompt(chunk_text, video_id)
                
                # LLM API 호출
                messages = [{"role": "user", "content": prompt}]
                response = await client.chat_completion(messages, temperature=0.7)
                
                # 응답에서 콘텐츠 추출
                content = await client.extract_content_from_response(response)
                
                # JSON 파싱
                parsed_result = json.loads(content)
                
                # 결과 검증 및 병합
                if "result" in parsed_result and isinstance(parsed_result["result"], dict):
                    chunk_words = parsed_result["result"]
                    
                    # 단어들을 소문자로 정규화하여 병합
                    for word, meanings in chunk_words.items():
                        word_lower = word.lower().strip()
                        if word_lower not in combined_result:
                            combined_result[word_lower] = []
                        
                        # 뜻 추가 (중복 제거)
                        if isinstance(meanings, list):
                            for meaning in meanings:
                                if meaning and meaning not in combined_result[word_lower]:
                                    combined_result[word_lower].append(meaning)
                        elif isinstance(meanings, str):
                            if meanings not in combined_result[word_lower]:
                                combined_result[word_lower].append(meanings)
                    
                    ACCESS_LOGGER.debug(f"Word Extraction Success for Chunk {idx}/{len(chunk_texts)} - Video ID: '{video_id}' - Words: {len(chunk_words)}")
                else:
                    ERROR_LOGGER.warning(f"Invalid Response Format for Chunk {idx}/{len(chunk_texts)} - Video ID: '{video_id}' - Response: {content[:200]}")
                    
            except json.JSONDecodeError as e:
                ERROR_LOGGER.error(f"JSON Parse Failed for Chunk {idx}/{len(chunk_texts)} - Video ID: '{video_id}' - Error: {str(e)}")
                # 계속 진행 (부분 실패 허용)
                continue
                
            except Exception as e:
                ERROR_LOGGER.error(f"Word Extraction Failed for Chunk {idx}/{len(chunk_texts)} - Video ID: '{video_id}' - Error: {str(e)}")
                # 계속 진행 (부분 실패 허용)
                continue
        
        # 최종 결과 구성
        final_result = {
            "videoId": video_id,
            "result": combined_result
        }
        
        ACCESS_LOGGER.info(f"End Word Extraction for Video ID: '{video_id}' - Total Words: {len(combined_result)}")
        return final_result
        
    except Exception as e:
        ERROR_LOGGER.error(f"Word Extraction Process Failed - Video ID: '{video_id}' - Error: {str(e)}")
        raise