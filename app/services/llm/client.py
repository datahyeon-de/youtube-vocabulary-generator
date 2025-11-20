import json          # JSON 파싱용
import asyncio
import httpx         # HTTP 클라이언트
from typing import Dict, List, Optional, Any  # 타입 힌팅
from app.core.config import settings  # 설정 가져오기
from app.core.logging import get_access_logger, get_error_logger  # 로깅

ACCESS_LOGGER = get_access_logger()
ERROR_LOGGER = get_error_logger()

class VLLMClient:
    """vLLM 서버와 통신하는 클라이언트"""
    def __init__(self):
        self.base_url = settings.VLLM_SERVER_URL
        self.endpoint = settings.VLLM_SERVER_ENDPOINT
        self.model = settings.VLLM_SERVER_MODEL
        self.timeout = settings.VLLM_SERVER_TIMEOUT
        self.max_retries = settings.VLLM_SERVER_MAX_RETRIES
        self.retry_delay = settings.VLLM_SERVER_RETRY_DELAY
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout)
        
        
    async def chat_completion(
        self, messages: List[Dict[str, Any]], temperature: float = 0.7, max_tokens: int = 4096
    ) -> Dict[str, Any]:
        """
        OpenAI 호환 chat comlpetion API 호출
        
        Args:
            messages: 대화 메시지 리스트 (예: [{"role": "user", "content": "..."}])
            temperature: 생성 온도 (0.0 ~ 2.0)
            max_tokens: 최대 토큰 수 
            
        Returns:
            API 응답 딕셔너리
            
        Raises:
            httpx.HTTPError: HTTP 요청 실패 시
            ValueError: JSON 파싱 실패 시
            Exception: 예상치 못한 오류 발생 시
        """
        url = f"{self.base_url}{self.endpoint}"
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        
        for attempt in range(1, self.max_retries + 1):
            try:
                ACCESS_LOGGER.info(f"Try vLLM API Call - Attempt: {attempt}/{self.max_retries}")
                response = await self.client.post(
                    url, json=payload, timeout=self.timeout
                )
                response.raise_for_status()
                
                result = response.json()
                ACCESS_LOGGER.info(f"Receive Success Response from vLLM API")
                return result
                
            except httpx.HTTPError as e:
                ERROR_LOGGER.error(f"vLLM API Call Failed - Attempt: {attempt}/{self.max_retries} - {str(e)}")
                if attempt < self.max_retries:
                    await asyncio.sleep(self.retry_delay * attempt)
                else:
                    raise
            except json.JSONDecodeError as e:
                ERROR_LOGGER.error(f"vLLM API Response Parse Failed: {str(e)} - {response.text}")
                raise ValueError(f"vLLM API 응답 파싱에 실패 했습니다.")
            except Exception as e:
                ERROR_LOGGER.error(f"Unexpected Error: {str(e)}")
                raise
    
    
    async def extract_content_from_response(
        self, response: Dict[str, Any]
    ) -> str:
        """
        API 응답에서 실제 생성된 텍스트 추출
        
        Args:
            response: API 응답 딕셔너리
            예시 응답 구조:
            {
                "id": "chatcmpl-6d1046ea79584b3f9bac2a7d2732fc67",
                ...
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "content": "[{\"word\":\"racing against the clock\",\"pos\":\"phrasal verb\",...}]",
                            ...
                        },
                        ...
                    }
                ],
                ...
            }
            
        Returns:
            생성된 텍스트 내용 (response["choices"][0]["message"]["content"])
        """
        try:
            # choices 배열 확인하기
            choices = response.get("choices", [])
            if not choices:
                raise ValueError("응답에 choices 배열이 없습니다.")
            
            # choices 배열에서 첫번재 message 확인하기
            message = choices[0].get("message", {})
            
            # message에서 content(실제 응답) 확인하기
            content = message.get("content", "")
            
            if not content:
                raise ValueError("응답에 content가 없습니다.")
            
            # content 양쪽 공백 제거하기
            return content.strip()
        
        except Exception as e:
            ERROR_LOGGER.error(f"Content Extraction Failed: {str(e)}")
            raise ValueError(f"응답 결과 추출에 실패했습니다.")


# 전역 변수로 클라이언트 인스턴스 저장
_vllm_client: Optional[VLLMClient] = None


async def get_vllm_client() -> VLLMClient:
    """
    vLLM 클라이언트 싱글톤 인스턴스 생성 및 반환
    - 하나의 클라이언트를 재사용하면 효율적으로 연결을 유지할 수 있음
    """
    global _vllm_client
    
    # 클라이언트가 없으면 새로 만들기
    if _vllm_client is None:
        _vllm_client = VLLMClient()
    
    # 이미 있을 경우에도 반환
    return _vllm_client


async def close_vllm_client():
    """
    vLLM 클라이언트 인스턴스 닫기
    """
    global _vllm_client
    if _vllm_client:
        await _vllm_client.client.aclose()
        _vllm_client = None