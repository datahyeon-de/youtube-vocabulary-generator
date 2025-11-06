"""
FastAPI 애플리케이션 메인 파일
"""
from fastapi import FastAPI
from app.routes import video

# FastAPI 앱 인스턴스 생성 (이게 웹 서버의 핵심!)
app = FastAPI(
    title="YouTube Vocabulary Generator",
    description="YouTube 동영상에서 단어장을 생성하는 API",
    version="0.1.0"
)


@app.get("/")
def read_root():
    """루트 경로 (메인 페이지)"""
    return {
        "message": "YouTube Vocabulary Generator API",
        "version": "0.1.0"
    }


@app.get("/health")
def health_check():
    """서버 상태 확인 엔드포인트"""
    return {"status": "ok"}


# 라우터 포함
app.include_router(video.router)
