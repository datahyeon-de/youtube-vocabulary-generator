"""
LLM 서비스 테스트 전용 fixture

vLLM 서버 연결 확인 및 테스트용 샘플 데이터를 제공합니다.
"""
import pytest
import httpx
from app.core.config import settings


# 테스트용 샘플 데이터
SAMPLE_CHUNK_TEXTS = [
    """
    Hello everyone, welcome to today's video. We're going to talk about artificial intelligence 
    and machine learning. These technologies are revolutionizing the way we work and live.
    """,
    """
    Let's dive into the details and explore how they can help us solve complex problems.
    We need to break the ice and start discussing these important topics.
    """,
    """
    Machine learning algorithms can make a decision based on large amounts of data.
    It's time to take a break and think about the implications of these technologies.
    """,
    """
    Companies across the globe are trying to keep pace with rapid innovation, so leaders often
    say we must think outside the box when tackling stubborn challenges in supply chains.
    """,
    """
    During product launches, marketing teams pull out all the stops to capture attention and
    avoid dropping the ball when customers have questions about pricing or warranties.
    """,
    """
    In remote teams, managers encourage teammates to touch base every Monday so no one feels
    left out in the cold when deadlines sneak up and priorities suddenly shift overnight.
    """,
    """
    When an outage happens, engineers jump through hoops to restore service, then circle back
    with postmortems so future incidents do not slip through the cracks unnoticed.
    """,
    """
    After major milestones, we like to take stock of lessons learned, connect the dots between
    data and strategy, and tee up the next set of experiments without biting off more than we can chew.
    """
]

SAMPLE_VIDEO_ID = "test_video_123"


@pytest.fixture
def sample_chunk_texts():
    """테스트용 샘플 청크 텍스트 리스트"""
    return SAMPLE_CHUNK_TEXTS


@pytest.fixture
def sample_video_id():
    """테스트용 샘플 Video ID"""
    return SAMPLE_VIDEO_ID


@pytest.fixture(scope="session")
def vllm_server_available():
    """vLLM 서버가 실행 중인지 확인하는 fixture
    
    Returns:
        bool: 서버가 사용 가능하면 True, 아니면 False
        
    확인 방법:
        - app/core/config.py의 VLLM_SERVER_URL 설정을 참고
        - 실제 API 엔드포인트(/v1/chat/completions)로 간단한 요청을 보내서 서버 실행 여부 확인
        
    사용 예시:
        @pytest.mark.skipif(not vllm_server_available(), reason="vLLM 서버가 실행 중이지 않습니다")
        def test_llm_function(vllm_server_available):
            # 테스트 코드
    """
    try:
        from app.core.config import settings
        
        # vLLM 서버 URL과 엔드포인트 가져오기
        base_url = settings.VLLM_SERVER_URL
        endpoint = settings.VLLM_SERVER_ENDPOINT
        api_url = f"{base_url}{endpoint}"
        
        # httpx를 사용하여 서버 연결 확인
        with httpx.Client(timeout=5.0) as client:
            try:
                # 1. /health 엔드포인트 시도 (vLLM이 제공하는 경우)
                health_url = f"{base_url}/health"
                try:
                    health_response = client.get(health_url, timeout=2.0)
                    if health_response.status_code == 200:
                        return True
                except (httpx.ConnectError, httpx.TimeoutException, httpx.NetworkError):
                    pass  # /health가 없으면 다음 방법 시도
                except Exception:
                    pass
                
                # 2. /v1/models 엔드포인트 시도 (OpenAI 호환 API)
                models_url = f"{base_url}/v1/models"
                try:
                    models_response = client.get(models_url, timeout=2.0)
                    if models_response.status_code == 200:
                        return True
                except (httpx.ConnectError, httpx.TimeoutException, httpx.NetworkError):
                    pass  # /v1/models가 없으면 다음 방법 시도
                except Exception:
                    pass
                
                # 3. 실제 API 엔드포인트로 간단한 요청을 보내서 서버 실행 여부 확인 (fallback)
                # 최소한의 요청으로 서버 응답 확인 (실제 처리는 하지 않음)
                test_payload = {
                    "model": settings.VLLM_SERVER_MODEL,
                    "messages": [{"role": "user", "content": "test"}],
                    "max_tokens": 1
                }
                response = client.post(api_url, json=test_payload, timeout=5.0)
                # 200 OK 또는 400 Bad Request (잘못된 요청)는 서버가 실행 중인 것으로 간주
                # 404, 500 등은 서버가 실행 중이지만 문제가 있는 경우
                # 연결 자체가 실패하면 서버가 실행 중이지 않은 것으로 간주
                return response.status_code in [200, 400]
            except (httpx.ConnectError, httpx.TimeoutException, httpx.NetworkError):
                # 연결 실패 시 False 반환
                return False
            except Exception:
                # 기타 예외 발생 시 False 반환
                return False
    except Exception:
        # 설정 로드 실패 등 기타 예외 발생 시 False 반환
        return False


@pytest.fixture
def skip_if_vllm_unavailable(vllm_server_available):
    """vLLM 서버가 사용 불가능하면 테스트를 스킵하는 fixture
    
    사용 예시:
        def test_llm_function(skip_if_vllm_unavailable):
            # vLLM 서버가 없으면 자동으로 스킵됨
            # 테스트 코드
    """
    if not vllm_server_available:
        pytest.skip("vLLM 서버가 실행 중이지 않습니다. 서버를 실행한 후 테스트를 다시 시도하세요.")
    return True

# ============================================================================
# A/B 테스트용 테스트 데이터
# ============================================================================

# A/B 테스트용 긴 청크 텍스트 (단어/숙어 적절한 비율)
AB_TEST_CHUNK_TEXT = """In today's rapidly evolving technological landscape, companies across various industries are constantly 
striving to stay ahead of the curve and maintain their competitive edge. Many organizations have come 
to realize that innovation is not just about developing cutting-edge products, but also about fostering 
a culture of continuous learning and adaptation.

However, the journey toward success is often fraught with challenges that require teams to think outside 
the box and develop creative solutions. Leaders must be willing to take calculated risks and make tough 
decisions, even when the path forward is uncertain. It's crucial to keep pace with market trends and 
customer expectations, as falling behind can lead to significant setbacks.

During product development cycles, teams often need to pull out all the stops to meet tight deadlines 
and deliver high-quality results. This requires careful planning, effective communication, and the ability 
to adapt quickly when unexpected issues arise. Project managers must ensure that nothing slips through 
the cracks, as even small oversights can have major consequences.

When facing complex problems, it's important to take a step back and look at the bigger picture. By 
connecting the dots between different pieces of information, teams can identify patterns and insights 
that might not be immediately obvious. Effective collaboration requires team members to touch base regularly 
and maintain open lines of communication. However, it's also important to avoid biting off more than you can chew.
"""

AB_TEST_VIDEO_ID = "ab_test_video_001"

# 단어 추출 결과 목업 (30~50개)
MOCK_WORD_EXTRACTION_RESULT = {
    "videoId": AB_TEST_VIDEO_ID,
    "result": {
        "innovation": {"품사": "n", "뜻": ["혁신", "창조"]},
        "technology": {"품사": "n", "뜻": ["기술", "과학기술"]},
        "evolving": {"품사": "adj", "뜻": ["발전하는", "변화하는"]},
        "landscape": {"품사": "n", "뜻": ["환경", "상황"]},
        "industries": {"품사": "n", "뜻": ["산업", "업종"]},
        "striving": {"품사": "v", "뜻": ["노력하다", "추구하다"]},
        "competitive": {"품사": "adj", "뜻": ["경쟁력 있는", "경쟁적인"]},
        "edge": {"품사": "n", "뜻": ["우위", "장점"]},
        "realize": {"품사": "v", "뜻": ["인식하다", "깨닫다"]},
        "cutting-edge": {"품사": "adj", "뜻": ["최첨단의", "혁신적인"]},
        "fostering": {"품사": "v", "뜻": ["촉진하다", "육성하다"]},
        "culture": {"품사": "n", "뜻": ["문화", "풍토"]},
        "continuous": {"품사": "adj", "뜻": ["연속적인", "계속되는"]},
        "learning": {"품사": "n", "뜻": ["학습", "습득"]},
        "adaptation": {"품사": "n", "뜻": ["적응", "변화"]},
        "journey": {"품사": "n", "뜻": ["여정", "과정"]},
        "success": {"품사": "n", "뜻": ["성공", "성취"]},
        "fraught": {"품사": "adj", "뜻": ["곤란한", "위험한"]},
        "challenges": {"품사": "n", "뜻": ["도전", "과제"]},
        "creative": {"품사": "adj", "뜻": ["창조적인", "창의적인"]},
        "solutions": {"품사": "n", "뜻": ["해결책", "방법"]},
        "leaders": {"품사": "n", "뜻": ["지도자", "리더"]},
        "willing": {"품사": "adj", "뜻": ["의향 있는", "기꺼이 하는"]},
        "calculated": {"품사": "adj", "뜻": ["계획적인", "계산된"]},
        "risks": {"품사": "n", "뜻": ["위험", "험담"]},
        "tough": {"품사": "adj", "뜻": ["힘든", "강한"]},
        "decisions": {"품사": "n", "뜻": ["결정", "판단"]},
        "uncertain": {"품사": "adj", "뜻": ["불확실한", "모호한"]},
        "crucial": {"품사": "adj", "뜻": ["중요한", "필수적인"]},
        "pace": {"품사": "n", "뜻": ["속도", "진행"]},
        "trends": {"품사": "n", "뜻": ["트렌드", "추세"]},
        "expectations": {"품사": "n", "뜻": ["기대", "예상"]},
        "setbacks": {"품사": "n", "뜻": ["장애", "애로사항"]},
        "development": {"품사": "n", "뜻": ["개발", "발전"]},
        "cycles": {"품사": "n", "뜻": ["주기", "순환"]},
        "deadlines": {"품사": "n", "뜻": ["마감일", "기한"]},
        "deliver": {"품사": "v", "뜻": ["전달하다", "제공하다"]},
        "planning": {"품사": "n", "뜻": ["계획", "준비"]},
        "effective": {"품사": "adj", "뜻": ["효과적인", "유용한"]},
        "communication": {"품사": "n", "뜻": ["통신", "소통"]},
        "ability": {"품사": "n", "뜻": ["능력", "재능"]},
        "adapt": {"품사": "v", "뜻": ["적응하다", "조정하다"]},
        "quickly": {"품사": "adv", "뜻": ["빠르게", "즉시"]},
        "unexpected": {"품사": "adj", "뜻": ["예상치 못한", "갑작스러운"]},
        "issues": {"품사": "n", "뜻": ["문제", "이슈"]},
        "ensure": {"품사": "v", "뜻": ["보장하다", "확인하다"]},
        "oversights": {"품사": "n", "뜻": ["소홀함", "생략"]},
        "consequences": {"품사": "n", "뜻": ["결과", "후과"]},
        "complex": {"품사": "adj", "뜻": ["복잡한", "다양한"]},
        "patterns": {"품사": "n", "뜻": ["패턴", "형태"]},
        "insights": {"품사": "n", "뜻": ["통찰", "이해"]},
        "collaboration": {"품사": "n", "뜻": ["협력", "협업"]}
    }
}

# 숙어 추출 결과 목업 (15~20개)
MOCK_PHRASE_EXTRACTION_RESULT = {
    "videoId": AB_TEST_VIDEO_ID,
    "result": {
        "stay ahead of the curve": "앞서 나가다",
        "think outside the box": "창의적으로 생각하다",
        "keep pace with": "따라잡다",
        "pull out all the stops": "모든 노력을 다하다",
        "slip through the cracks": "소홀히 하다",
        "take a step back": "한 걸음 물러서다",
        "look at the bigger picture": "전체를 보다",
        "connect the dots": "연결하다",
        "touch base": "상의하다",
        "bite off more than you can chew": "무리하게 받다",
        "falling behind": "뒤처지다",
        "make tough decisions": "어려운 결정을 내리다",
        "meet tight deadlines": "빡빡한 마감일을 맞추다",
        "deliver high-quality results": "고품질 결과를 제공하다",
        "maintain open lines": "열린 소통을 유지하다",
        "identify patterns": "패턴을 식별하다",
        "develop creative solutions": "창의적인 해결책을 개발하다",
        "take calculated risks": "계산된 위험을 감수하다"
    }
}


@pytest.fixture
def ab_test_chunk_text():
    """A/B 테스트용 긴 청크 텍스트"""
    return AB_TEST_CHUNK_TEXT


@pytest.fixture
def ab_test_video_id():
    """A/B 테스트용 Video ID"""
    return AB_TEST_VIDEO_ID


@pytest.fixture
def mock_word_extraction_result():
    """A/B 테스트용 단어 추출 결과 목업"""
    return MOCK_WORD_EXTRACTION_RESULT


@pytest.fixture
def mock_phrase_extraction_result():
    """A/B 테스트용 숙어 추출 결과 목업"""
    return MOCK_PHRASE_EXTRACTION_RESULT
