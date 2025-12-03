"""
에러 로깅 유틸리티

에러 발생 위치와 상세 정보를 로깅하는 재사용 가능한 헬퍼 함수들
"""
import inspect
import traceback
from typing import Optional
from app.core.logging import get_error_logger

ERROR_LOGGER = get_error_logger()


def get_error_location() -> tuple[str, int, str]:
    """
    현재 실행 중인 코드의 위치 정보를 반환합니다.
    
    Returns:
        tuple: (파일명, 줄 번호, 함수명)
    """
    frame = inspect.currentframe()
    # 호출한 함수의 프레임을 가져오기 위해 한 단계 위로
    caller_frame = frame.f_back.f_back if (frame and frame.f_back) else None
    if caller_frame:
        filename = caller_frame.f_code.co_filename
        line_number = caller_frame.f_lineno
        function_name = caller_frame.f_code.co_name
    else:
        filename = "unknown"
        line_number = 0
        function_name = "unknown"
    
    return filename, line_number, function_name


def log_error_with_location(
    error_type: str,
    message: str,
    error: Optional[Exception] = None,
    additional_info: Optional[dict] = None
) -> str:
    """
    에러 발생 위치와 상세 정보를 포함한 에러 메시지를 생성하고 로깅합니다.
    
    Args:
        error_type: 에러 타입 (예: "JSON Parse Failed", "Empty Response")
        message: 기본 에러 메시지
        error: 발생한 예외 객체 (선택사항)
        additional_info: 추가 정보 딕셔너리 (선택사항)
        
    Returns:
        생성된 에러 메시지 문자열
    """
    filename, line_number, function_name = get_error_location()
    
    error_msg_parts = [
        f"{error_type}",
        f"Error Location: {filename}:{line_number} in {function_name}()",
        f"Error: {message}"
    ]
    
    if error:
        error_msg_parts.append(f"Exception: {str(error)}")
        error_msg_parts.append(f"Traceback:\n{traceback.format_exc()}")
    
    if additional_info:
        for key, value in additional_info.items():
            error_msg_parts.append(f"{key}: {value}")
    
    error_msg = "\n".join(error_msg_parts)
    ERROR_LOGGER.error(error_msg)
    
    return error_msg

