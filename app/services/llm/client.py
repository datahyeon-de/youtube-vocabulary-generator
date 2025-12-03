import json          # JSON 파싱용
import asyncio
import httpx         # HTTP 클라이언트
from typing import Dict, List, Optional, Any  # 타입 힌팅
from app.core.config import settings  # 설정 가져오기
from app.core.logging import get_access_logger, get_error_logger  # 로깅
from app.core.error_utils import log_error_with_location

ACCESS_LOGGER = get_access_logger()
ERROR_LOGGER = get_error_logger()

class VLLMClient:
    """vLLM 서버와 통신하는 클라이언트 (컨텍스트 매니저)"""
    def __init__(self):
        self.base_url = settings.VLLM_SERVER_URL
        self.endpoint = settings.VLLM_SERVER_ENDPOINT
        self.model = settings.VLLM_SERVER_MODEL
        self.timeout = settings.VLLM_SERVER_TIMEOUT
        self.max_retries = settings.VLLM_SERVER_MAX_RETRIES
        self.retry_delay = settings.VLLM_SERVER_RETRY_DELAY
        self.client: Optional[httpx.AsyncClient] = None
    
    async def __aenter__(self):
        """컨텍스트 매니저 진입 시 클라이언트 생성"""
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """컨텍스트 매니저 종료 시 클라이언트 정리"""
        if self.client:
            await self.client.aclose()
            self.client = None
        return False  # 예외를 전파
        
        
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
        
        if not self.client:
            raise RuntimeError("VLLMClient는 컨텍스트 매니저로 사용해야 합니다. 'async with VLLMClient() as client:' 형식을 사용하세요.")
        
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
                log_error_with_location(
                    "Missing Choices Array",
                    "응답에 choices 배열이 없습니다.",
                    additional_info={
                        "Response Keys": list(response.keys()),
                        "Response (first 1000 chars)": str(response)[:1000]
                    }
                )
                raise ValueError("응답에 choices 배열이 없습니다.")
            
            # choices 배열에서 첫번재 message 확인하기
            message = choices[0].get("message", {})
            if not message:
                log_error_with_location(
                    "Missing Message",
                    "응답에 message가 없습니다.",
                    additional_info={
                        "Choices[0] Keys": list(choices[0].keys()) if choices else 'N/A',
                        "Choices[0] (first 500 chars)": str(choices[0])[:500] if choices else 'N/A'
                    }
                )
                raise ValueError("응답에 message가 없습니다.")
            
            # message에서 content(실제 응답) 확인하기
            content = message.get("content", "")
            
            if not content:
                log_error_with_location(
                    "Missing Content",
                    "응답에 content가 없습니다.",
                    additional_info={
                        "Message Keys": list(message.keys()),
                        "Message (first 500 chars)": str(message)[:500]
                    }
                )
                raise ValueError("응답에 content가 없습니다.")
            
            # content 양쪽 공백 제거하기
            content_stripped = content.strip()
            
            # 마크다운 코드 블록 제거 (```json ... ``` 또는 ``` ... ```)
            if content_stripped.startswith("```"):
                # 첫 번째 ``` 제거
                if content_stripped.startswith("```json"):
                    content_stripped = content_stripped[7:]  # ```json 제거
                elif content_stripped.startswith("```"):
                    content_stripped = content_stripped[3:]  # ``` 제거
                
                # 마지막 ``` 제거
                if content_stripped.endswith("```"):
                    content_stripped = content_stripped[:-3]
                
                # 다시 공백 제거
                content_stripped = content_stripped.strip()
            
            # 빈 응답인 경우 로깅
            if not content_stripped:
                log_error_with_location(
                    "Empty Response Content",
                    "응답 content가 비어있습니다.",
                    additional_info={
                        "Original Content Length": len(content),
                        "Message": str(message)[:500]
                    }
                )
                raise ValueError("응답 content가 비어있습니다.")
            
            return content_stripped
        
        except ValueError:
            # ValueError는 이미 상세히 로깅되었으므로 재발생
            raise
        except Exception as e:
            # 예상치 못한 예외 발생 시 상세 정보 로깅
            log_error_with_location(
                "Content Extraction Failed",
                f"응답 결과 추출에 실패했습니다: {str(e)}",
                error=e,
                additional_info={
                    "Response Type": str(type(response)),
                    "Response Keys": list(response.keys()) if isinstance(response, dict) else 'N/A',
                    "Response (first 1000 chars)": str(response)[:1000]
                }
            )
            raise ValueError(f"응답 결과 추출에 실패했습니다: {str(e)}")

