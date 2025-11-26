"""
단어 추출 모듈 테스트

app/services/llm/extract_words.py의 단어 추출 기능을 테스트합니다.
"""
import pytest
from app.services.llm.extract_words import extract_words_from_chunks


# ============================================================================
# 정상 케이스 테스트
# ============================================================================

@pytest.mark.asyncio
async def test_extract_words_from_chunks_success(
    skip_if_vllm_unavailable,
    sample_chunk_texts,
    sample_video_id
):
    """정상적인 청크 텍스트로 단어 추출 시 성공 응답 테스트
    
    테스트 대상:
        - app/services/llm/extract_words.py의 extract_words_from_chunks 함수
        - 여러 청크를 병렬로 처리하여 단어 추출
        
    검증 내용:
        - 응답에 videoId 필드 포함
        - 응답에 result 필드 포함 (딕셔너리)
        - result에 단어들이 포함되어 있음
        - 각 단어의 구조가 올바름 (품사, 뜻 포함)
    """
    # Arrange (준비): fixture에서 샘플 데이터 가져오기
    chunk_texts = sample_chunk_texts
    video_id = sample_video_id
    
    # Act (실행): 단어 추출 함수 호출
    result = await extract_words_from_chunks(chunk_texts, video_id)
    
    # Assert (검증): 결과 확인
    assert result is not None
    assert isinstance(result, dict)
    assert "videoId" in result
    assert result["videoId"] == video_id
    assert "result" in result
    assert isinstance(result["result"], dict)
    
    # 단어가 추출되었는지 확인
    words = result["result"]
    assert len(words) > 0, "단어가 추출되지 않았습니다."
    
    # 샘플 단어의 구조 확인
    sample_word = list(words.items())[0]
    word_key, word_data = sample_word
    
    # 단어 키는 문자열이어야 함
    assert isinstance(word_key, str)
    assert len(word_key) > 0
    
    # 단어 데이터는 딕셔너리여야 함
    assert isinstance(word_data, dict)
    
    # 품사와 뜻 필드 확인
    if "품사" in word_data:
        assert isinstance(word_data["품사"], str)
    
    if "뜻" in word_data:
        assert isinstance(word_data["뜻"], list)
        assert len(word_data["뜻"]) > 0
        # 뜻은 모두 문자열이어야 함
        for meaning in word_data["뜻"]:
            assert isinstance(meaning, str)
            assert len(meaning) > 0


@pytest.mark.asyncio
async def test_extract_words_from_chunks_empty_chunks(
    skip_if_vllm_unavailable,
    sample_video_id
):
    """빈 청크 리스트로 단어 추출 시 빈 결과 반환 테스트
    
    테스트 대상:
        - 빈 청크 리스트 처리
        
    검증 내용:
        - 응답 구조는 올바르지만 result가 빈 딕셔너리
    """
    # Arrange (준비): 빈 청크 리스트
    chunk_texts = []
    video_id = sample_video_id
    
    # Act (실행): 단어 추출 함수 호출
    result = await extract_words_from_chunks(chunk_texts, video_id)
    
    # Assert (검증): 빈 결과 확인
    assert result is not None
    assert isinstance(result, dict)
    assert "videoId" in result
    assert result["videoId"] == video_id
    assert "result" in result
    assert isinstance(result["result"], dict)
    assert len(result["result"]) == 0


@pytest.mark.asyncio
async def test_extract_words_from_chunks_single_chunk(
    skip_if_vllm_unavailable,
    sample_video_id
):
    """단일 청크로 단어 추출 시 성공 응답 테스트
    
    테스트 대상:
        - 단일 청크 처리
        
    검증 내용:
        - 단일 청크도 정상적으로 처리됨
    """
    # Arrange (준비): 단일 청크
    chunk_texts = [
        "Hello everyone, welcome to today's video. We're going to talk about artificial intelligence."
    ]
    video_id = sample_video_id
    
    # Act (실행): 단어 추출 함수 호출
    result = await extract_words_from_chunks(chunk_texts, video_id)
    
    # Assert (검증): 결과 확인
    assert result is not None
    assert isinstance(result, dict)
    assert "videoId" in result
    assert result["videoId"] == video_id
    assert "result" in result
    assert isinstance(result["result"], dict)
    assert len(result["result"]) > 0


# ============================================================================
# 결과 구조 검증 테스트
# ============================================================================

@pytest.mark.asyncio
async def test_extract_words_result_structure(
    skip_if_vllm_unavailable,
    sample_chunk_texts,
    sample_video_id
):
    """단어 추출 결과 구조 검증 테스트
    
    테스트 대상:
        - 결과 딕셔너리의 구조가 올바른지 확인
        
    검증 내용:
        - 모든 단어가 올바른 구조를 가지고 있음
        - 품사는 "n", "v", "adj", "adv" 중 하나
        - 뜻은 리스트이며 최대 2개
    """
    # Arrange (준비)
    chunk_texts = sample_chunk_texts
    video_id = sample_video_id
    
    # Act (실행)
    result = await extract_words_from_chunks(chunk_texts, video_id)
    
    # Assert (검증): 결과 구조 확인
    words = result["result"]
    
    valid_pos = {"n", "v", "adj", "adv", ""}  # 빈 문자열도 허용 (구버전 호환)
    
    for word, word_data in words.items():
        # 단어 키 검증
        assert isinstance(word, str)
        assert len(word) > 0
        
        # 단어 데이터 검증
        assert isinstance(word_data, dict)
        
        # 품사 검증 (있는 경우)
        if "품사" in word_data:
            pos = word_data["품사"]
            assert isinstance(pos, str)
            # 품사가 있으면 유효한 값이어야 함
            if pos:
                assert pos in valid_pos, f"유효하지 않은 품사: {pos}"
        
        # 뜻 검증
        if "뜻" in word_data:
            meanings = word_data["뜻"]
            assert isinstance(meanings, list)
            # 최대 2개까지만 허용
            assert len(meanings) <= 2, f"뜻이 2개를 초과함: {word} - {meanings}"
            # 각 뜻은 문자열이어야 함
            for meaning in meanings:
                assert isinstance(meaning, str)
                assert len(meaning) > 0
    
    # 결과 출력 (테스트 확인용)
    print("\n" + "="*80)
    print(f"[단어 추출 결과] 총 {len(words)}개 단어 추출됨")
    print("="*80)
    
    # 처음 5개와 마지막 5개 단어 출력
    word_items = list(words.items())
    print("\n[처음 5개 단어]")
    for i, (word, word_data) in enumerate(word_items[:5], 1):
        pos = word_data.get("품사", "N/A")
        meanings = word_data.get("뜻", [])
        meanings_str = ", ".join(meanings) if meanings else "N/A"
        print(f"  {i}. {word} ({pos}): {meanings_str}")
    
    if len(word_items) > 10:
        print("\n... (중간 생략) ...\n")
    
    print("\n[마지막 5개 단어]")
    for i, (word, word_data) in enumerate(word_items[-5:], len(word_items) - 4):
        pos = word_data.get("품사", "N/A")
        meanings = word_data.get("뜻", [])
        meanings_str = ", ".join(meanings) if meanings else "N/A"
        print(f"  {i}. {word} ({pos}): {meanings_str}")
    
    # 마지막 단어 상세 출력
    if word_items:
        last_word, last_word_data = word_items[-1]
        print(f"\n[마지막 단어 상세]")
        print(f"  단어: {last_word}")
        print(f"  품사: {last_word_data.get('품사', 'N/A')}")
        print(f"  뜻: {last_word_data.get('뜻', [])}")
        print(f"  전체 데이터: {last_word_data}")
    print("="*80 + "\n")

