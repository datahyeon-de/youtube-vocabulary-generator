"""
FastAPI 미들웨어 모듈
요청/응답 로깅 및 공통 처리 로직을 담당합니다.
"""
import time
import json
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logging import get_access_logger, get_error_logger

# 로거 가져오기
access_logger = get_access_logger()
error_logger = get_error_logger()


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    HTTP 요청/응답을 로깅하는 미들웨어
    
    모든 요청에 대해 다음 정보를 기록합니다:
    - 클라이언트 IP 주소
    - HTTP 메서드
    - 요청 경로
    - 쿼리 파라미터
    - 응답 상태 코드
    - 처리 시간
    - 요청 헤더 (민감 정보 제외)
    """
    
    async def dispatch(self, request: Request, call_next):
        """
        미들웨어의 핵심 메서드
        요청 전후 처리를 담당합니다.
        
        Args:
            request: FastAPI Request 객체
            call_next: 다음 미들웨어 또는 라우터로 요청을 전달하는 함수
            
        Returns:
            Response: 처리된 응답 객체
        """
        # 요청 시작 시간 기록
        started_at = time.time()
        
        # 요청 정보 수집
        client_host = request.client.host if request.client else "unknown"
        method = request.method
        url_path = request.url.path
        query_string = request.url.query
        
        # 헤더 정보 수집 (딕셔너리로 변환)
        headers = dict(request.headers)
        
        # 민감한 헤더 제거 (보안을 위해)
        sensitive_headers = ["authorization", "cookie", "x-api-key"]
        filtered_headers = {
            k: v for k, v in headers.items() 
            if k.lower() not in sensitive_headers
        }
        
        # 요청 처리 (실제 라우터 실행)
        try:
            response = await call_next(request)
            status_code = response.status_code
            error_occurred = False
        except Exception as e:
            # 예외 발생 시 에러 로깅
            error_occurred = True
            status_code = 500
            error_logger.error(
                f"요청 처리 중 오류 발생: {method} {url_path} - {str(e)}",
                exc_info=True
            )
            # 예외를 다시 발생시켜서 FastAPI의 기본 에러 핸들링이 동작하도록 함
            raise
        
        # 처리 시간 계산 (밀리초)
        process_time = (time.time() - started_at) * 1000
        
        # 로그 데이터 구성
        log_data = {
            "remote_addr": client_host,
            "method": method,
            "path": url_path,
            "query": query_string if query_string else None,
            "status_code": status_code,
            "latency_ms": round(process_time, 2),
            "headers": filtered_headers,
            "error": error_occurred
        }
        
        # 접근 로그 기록 (JSON 형태로 저장하면 나중에 파싱하기 쉬움)
        access_logger.info(json.dumps(log_data, ensure_ascii=False))
        
        # 응답 헤더에 처리 시간 추가 (선택사항)
        response.headers["X-Process-Time"] = str(round(process_time, 2))
        
        return response


def setup_middleware(app):
    """
    FastAPI 애플리케이션에 미들웨어를 등록합니다.
    
    Args:
        app: FastAPI 애플리케이션 인스턴스
        
    Returns:
        app: 미들웨어가 등록된 애플리케이션 인스턴스
    """
    app.add_middleware(LoggingMiddleware)
    return app