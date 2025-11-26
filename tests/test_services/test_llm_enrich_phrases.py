"""
숙어 예문 생성 모듈 테스트

app/services/llm/enrich_phrases.py의 숙어 예문 생성 기능을 테스트합니다.
"""
import pytest
from app.services.llm.extract_phrases import extract_phrases_from_chunks
from app.services.llm.enrich_phrases import enrich_phrases


# ============================================================================
# 정상 케이스 테스트
# ============================================================================

@pytest.mark.asyncio
async def test_enrich_phrases_success(
    skip_if_vllm_unavailable,
    sample_chunk_texts,
    sample_video_id
):
    """정상적인 1단계 결과로 숙어 예문 생성 시 성공 응답 테스트
    
    테스트 대상:
        - app/services/llm/enrich_phrases.py의 enrich_phrases 함수
        - 1단계 숙어 추출 결과에 예문 추가
        
    검증 내용:
        - 응답에 videoId 필드 포함
        - 응답에 result 필드 포함 (딕셔너리)
        - 각 숙어에 예문이 포함됨
    """
    # Arrange (준비): 1단계 숙어 추출 결과 생성
    phrase_extraction_result = await extract_phrases_from_chunks(
        sample_chunk_texts, sample_video_id
    )
    
    # 숙어가 추출되었는지 확인 (숙어가 없을 수도 있음)
    phrases = phrase_extraction_result.get("result", {})
    
    # 숙어가 없는 경우 테스트 스킵
    if len(phrases) == 0:
        pytest.skip("1단계에서 숙어가 추출되지 않았습니다. 테스트를 스킵합니다.")
    
    # Act (실행): 숙어 예문 생성 함수 호출
    result = await enrich_phrases(phrase_extraction_result, sample_video_id)
    
    # Assert (검증): 결과 확인
    assert result is not None
    assert isinstance(result, dict)
    assert "videoId" in result
    assert result["videoId"] == sample_video_id
    assert "result" in result
    assert isinstance(result["result"], dict)
    
    # 예문이 생성되었는지 확인
    enriched_phrases = result["result"]
    assert len(enriched_phrases) > 0
    
    # 샘플 숙어의 예문 구조 확인
    sample_phrase = list(enriched_phrases.items())[0]
    phrase_key, phrase_data = sample_phrase
    
    # 숙어 키는 문자열이어야 함
    assert isinstance(phrase_key, str)
    assert len(phrase_key) > 0
    
    # 숙어 데이터는 딕셔너리여야 함
    assert isinstance(phrase_data, dict)
    
    # 예문 필드 확인
    assert "예문" in phrase_data
    example = phrase_data["예문"]
    assert isinstance(example, str)
    assert len(example) > 0


@pytest.mark.asyncio
async def test_enrich_phrases_empty_result(
    skip_if_vllm_unavailable,
    sample_video_id
):
    """빈 1단계 결과로 예문 생성 시 빈 결과 반환 테스트
    
    테스트 대상:
        - 빈 1단계 결과 처리
        
    검증 내용:
        - 응답 구조는 올바르지만 result가 빈 딕셔너리
    """
    # Arrange (준비): 빈 1단계 결과
    phrase_extraction_result = {
        "videoId": sample_video_id,
        "result": {}
    }
    
    # Act (실행): 숙어 예문 생성 함수 호출
    result = await enrich_phrases(phrase_extraction_result, sample_video_id)
    
    # Assert (검증): 빈 결과 확인
    assert result is not None
    assert isinstance(result, dict)
    assert "videoId" in result
    assert result["videoId"] == sample_video_id
    assert "result" in result
    assert isinstance(result["result"], dict)
    assert len(result["result"]) == 0


# ============================================================================
# 결과 구조 검증 테스트
# ============================================================================

@pytest.mark.asyncio
async def test_enrich_phrases_result_structure(
    skip_if_vllm_unavailable,
    sample_chunk_texts,
    sample_video_id
):
    """숙어 예문 결과 구조 검증 테스트
    
    테스트 대상:
        - 결과 딕셔너리의 구조가 올바른지 확인
        
    검증 내용:
        - 모든 숙어에 예문이 포함됨
        - 예문은 영어 문자열
    """
    # Arrange (준비): 1단계 결과 생성
    phrase_extraction_result = await extract_phrases_from_chunks(
        sample_chunk_texts, sample_video_id
    )
    
    phrases = phrase_extraction_result.get("result", {})
    
    # 숙어가 없는 경우 테스트 스킵
    if len(phrases) == 0:
        pytest.skip("1단계에서 숙어가 추출되지 않았습니다. 테스트를 스킵합니다.")
    
    # Act (실행): 예문 생성
    result = await enrich_phrases(phrase_extraction_result, sample_video_id)
    
    # Assert (검증): 결과 구조 확인
    enriched_phrases = result["result"]
    
    for phrase, phrase_data in enriched_phrases.items():
        # 숙어 키 검증
        assert isinstance(phrase, str)
        assert len(phrase) > 0
        
        # 숙어 데이터 검증
        assert isinstance(phrase_data, dict)
        
        # 예문 검증
        assert "예문" in phrase_data
        example = phrase_data["예문"]
        assert isinstance(example, str)
        assert len(example) > 0
    
    # 결과 출력 (테스트 확인용)
    print("\n" + "="*80)
    print(f"[숙어 예문 생성 결과] 총 {len(enriched_phrases)}개 숙어 처리됨")
    print("="*80)
    
    # 처음 5개와 마지막 5개 숙어 출력
    phrase_items = list(enriched_phrases.items())
    print("\n[처음 5개 숙어 예문]")
    for i, (phrase, phrase_data) in enumerate(phrase_items[:5], 1):
        example = phrase_data.get("예문", "N/A")
        print(f"  {i}. {phrase}")
        print(f"      예문: {example}")
    
    if len(phrase_items) > 10:
        print("\n... (중간 생략) ...\n")
    
    print("\n[마지막 5개 숙어 예문]")
    for i, (phrase, phrase_data) in enumerate(phrase_items[-5:], len(phrase_items) - 4):
        example = phrase_data.get("예문", "N/A")
        print(f"  {i}. {phrase}")
        print(f"      예문: {example}")
    
    # 마지막 숙어 상세 출력
    if phrase_items:
        last_phrase, last_phrase_data = phrase_items[-1]
        print(f"\n[마지막 숙어 상세]")
        print(f"  숙어: {last_phrase}")
        print(f"  예문: {last_phrase_data.get('예문', 'N/A')}")
        print(f"  전체 데이터: {last_phrase_data}")
    print("="*80 + "\n")

