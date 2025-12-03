"""
단어 상세 정보 생성 모듈 테스트

app/services/llm/enrich_words.py의 단어 상세 정보 생성 기능을 테스트합니다.
"""
import pytest
from app.services.llm.extract_words import extract_words_from_chunks
from app.services.llm.enrich_words import enrich_words


# ============================================================================
# 정상 케이스 테스트
# ============================================================================

@pytest.mark.asyncio
async def test_enrich_words_success(
    skip_if_vllm_unavailable,
    sample_chunk_texts,
    sample_video_id
):
    """정상적인 1단계 결과로 단어 상세 정보 생성 시 성공 응답 테스트
    
    테스트 대상:
        - app/services/llm/enrich_words.py의 enrich_words 함수
        - 1단계 단어 추출 결과에 동의어와 예문 추가
        
    검증 내용:
        - 응답에 videoId 필드 포함
        - 응답에 result 필드 포함 (딕셔너리)
        - 각 단어에 동의어와 예문이 포함됨
    """
    # Arrange (준비): 1단계 단어 추출 결과 생성
    word_extraction_result = await extract_words_from_chunks(
        sample_chunk_texts, sample_video_id
    )
    
    # 단어가 추출되었는지 확인
    assert len(word_extraction_result.get("result", {})) > 0, "1단계에서 단어가 추출되지 않았습니다."
    
    # Act (실행): 단어 상세 정보 생성 함수 호출
    result = await enrich_words(word_extraction_result, sample_video_id)
    
    # Assert (검증): 결과 확인
    assert result is not None
    assert isinstance(result, dict)
    assert "videoId" in result
    assert result["videoId"] == sample_video_id
    assert "result" in result
    assert isinstance(result["result"], dict)
    
    # 상세 정보가 생성되었는지 확인
    enriched_words = result["result"]
    assert len(enriched_words) > 0
    
    # 샘플 단어의 상세 정보 구조 확인
    sample_word = list(enriched_words.items())[0]
    word_key, word_data = sample_word
    
    # 단어 키는 문자열이어야 함
    assert isinstance(word_key, str)
    assert len(word_key) > 0
    
    # 단어 데이터는 딕셔너리여야 함
    assert isinstance(word_data, dict)
    
    # 동의어 필드 확인
    assert "동의어" in word_data
    synonyms = word_data["동의어"]
    assert isinstance(synonyms, list)
    # 최대 2개까지만 허용
    assert len(synonyms) <= 2, f"동의어가 2개를 초과함: {word_key} - {synonyms}"
    # 각 동의어는 영어 문자열이어야 함
    for synonym in synonyms:
        assert isinstance(synonym, str)
        assert len(synonym) > 0
    
    # 예문 필드 확인
    assert "예문" in word_data
    example = word_data["예문"]
    assert isinstance(example, str)
    assert len(example) > 0


@pytest.mark.asyncio
async def test_enrich_words_empty_result(
    skip_if_vllm_unavailable,
    sample_video_id
):
    """빈 1단계 결과로 상세 정보 생성 시 빈 결과 반환 테스트
    
    테스트 대상:
        - 빈 1단계 결과 처리
        
    검증 내용:
        - 응답 구조는 올바르지만 result가 빈 딕셔너리
    """
    # Arrange (준비): 빈 1단계 결과
    word_extraction_result = {
        "videoId": sample_video_id,
        "result": {}
    }
    
    # Act (실행): 단어 상세 정보 생성 함수 호출
    result = await enrich_words(word_extraction_result, sample_video_id)
    
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
async def test_enrich_words_result_structure(
    skip_if_vllm_unavailable,
    sample_chunk_texts,
    sample_video_id
):
    """단어 상세 정보 결과 구조 검증 테스트
    
    테스트 대상:
        - 결과 딕셔너리의 구조가 올바른지 확인
        
    검증 내용:
        - 모든 단어에 동의어와 예문이 포함됨
        - 동의어는 최대 2개
        - 예문은 영어 문자열
    """
    # Arrange (준비): 1단계 결과 생성
    word_extraction_result = await extract_words_from_chunks(
        sample_chunk_texts, sample_video_id
    )
    
    # Act (실행): 상세 정보 생성
    result = await enrich_words(word_extraction_result, sample_video_id)
    
    # Assert (검증): 결과 구조 확인
    enriched_words = result["result"]
    
    for word, word_data in enriched_words.items():
        # 단어 키 검증
        assert isinstance(word, str)
        assert len(word) > 0
        
        # 단어 데이터 검증
        assert isinstance(word_data, dict)
        
        # 동의어 검증
        assert "동의어" in word_data
        synonyms = word_data["동의어"]
        assert isinstance(synonyms, list)
        assert len(synonyms) <= 2, f"동의어가 2개를 초과함: {word} - {synonyms}"
        for synonym in synonyms:
            assert isinstance(synonym, str)
            assert len(synonym) > 0
        
        # 예문 검증
        assert "예문" in word_data
        example = word_data["예문"]
        assert isinstance(example, str)
        assert len(example) > 0
    
    # 결과 출력 (테스트 확인용)
    print("\n" + "="*80)
    print(f"[단어 상세 정보 생성 결과] 총 {len(enriched_words)}개 단어 처리됨")
    print("="*80)
    
    # 처음 5개와 마지막 5개 단어 출력
    word_items = list(enriched_words.items())
    print("\n[처음 5개 단어 상세 정보]")
    for i, (word, word_data) in enumerate(word_items[:5], 1):
        synonyms = word_data.get("동의어", [])
        example = word_data.get("예문", "N/A")
        synonyms_str = ", ".join(synonyms) if synonyms else "N/A"
        print(f"  {i}. {word}")
        print(f"      동의어: {synonyms_str}")
        print(f"      예문: {example}")
    
    if len(word_items) > 10:
        print("\n... (중간 생략) ...\n")
    
    print("\n[마지막 5개 단어 상세 정보]")
    for i, (word, word_data) in enumerate(word_items[-5:], len(word_items) - 4):
        synonyms = word_data.get("동의어", [])
        example = word_data.get("예문", "N/A")
        synonyms_str = ", ".join(synonyms) if synonyms else "N/A"
        print(f"  {i}. {word}")
        print(f"      동의어: {synonyms_str}")
        print(f"      예문: {example}")
    
    # 마지막 단어 상세 출력
    if word_items:
        last_word, last_word_data = word_items[-1]
        print(f"\n[마지막 단어 상세]")
        print(f"  단어: {last_word}")
        print(f"  동의어: {last_word_data.get('동의어', [])}")
        print(f"  예문: {last_word_data.get('예문', 'N/A')}")
        print(f"  전체 데이터: {last_word_data}")
    print("="*80 + "\n")

