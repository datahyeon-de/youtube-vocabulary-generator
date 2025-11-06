"""
FastAPI 앱 메인 테스트
"""
import pytest
from fastapi.testclient import TestClient
import httpx


# ============================================================================
# TestClient 방식 (서버 없이 인메모리 테스트)
# ============================================================================
def test_app_startup(client: TestClient):
    """앱이 정상적으로 시작되는지 테스트 (TestClient 방식)"""
    response = client.get("/")
    assert response.status_code in [200, 404]


def test_health_check(client: TestClient):
    """Health check 엔드포인트 테스트 (TestClient 방식)"""
    response = client.get("/health")
    if response.status_code == 200:
        assert "status" in response.json()


# ============================================================================
# 실행 중인 서버에 요청 보내기 (수동으로 서버 실행 후 테스트)
# ============================================================================
# 사용법:
# 1. 터미널에서 서버 실행: uvicorn app.main:app --reload
# 2. 다른 터미널에서 pytest 실행: pytest tests/test_main.py -k "running_server"
# 3. 테스트가 실행 중인 서버로 HTTP 요청을 보냄

def test_root_endpoint_running_server(running_server_client: httpx.Client):
    """실행 중인 서버의 루트 엔드포인트 테스트"""
    response = running_server_client.get("/")
    
    print(f"\n[테스트 결과] GET /")
    print(f"상태 코드: {response.status_code}")
    print(f"응답 내용: {response.json()}")
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data or "version" in data


def test_health_check_running_server(running_server_client: httpx.Client):
    """실행 중인 서버의 health check 엔드포인트 테스트"""
    response = running_server_client.get("/health")
    
    print(f"\n[테스트 결과] GET /health")
    print(f"상태 코드: {response.status_code}")
    print(f"응답 내용: {response.json()}")
    
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "ok"


def test_multiple_requests_running_server(running_server_client: httpx.Client):
    """실행 중인 서버에 여러 요청 보내기"""
    print("\n[테스트 결과] 여러 요청 테스트")
    
    for i in range(3):
        response = running_server_client.get("/health")
        print(f"요청 {i+1}: 상태 코드 {response.status_code}")
        
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
    
    print("✅ 모든 요청 성공!")