"""
LLM 프롬프트 모듈 테스트

단어/숙어 추출 프롬프트에 새로 추가된 규칙이 포함되어 있는지 검증합니다.
"""
from app.services.llm import prompts


def test_word_prompt_enforces_unique_meanings():
    """단어 추출 프롬프트가 중복 의미 제거 규칙을 안내하는지 확인"""
    chunk = "Sample text about innovation and collaboration."
    video_id = "vid"
    prompt_text = prompts.get_word_extraction_prompt(chunk, video_id)

    assert "중복" in prompt_text
    assert "최대 2개" in prompt_text
    assert "하나만 유지" in prompt_text


def test_phrase_prompt_enforces_multi_token_rule():
    """숙어 추출 프롬프트가 다단어 표현만 허용하도록 안내하는지 확인"""
    chunk = "Sample text about innovation and collaboration."
    video_id = "vid"
    prompt_text = prompts.get_phrase_extraction_prompt(chunk, video_id)

    assert "두 단어 이상" in prompt_text
    assert "단일 단어" in prompt_text
    assert "최소 두 개" in prompt_text

