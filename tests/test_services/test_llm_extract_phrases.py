"""
숙어 추출 모듈 테스트

app/services/llm/extract_phrases.py의 숙어 추출 기능을 테스트합니다.
"""
import pytest
from app.services.llm.extract_phrases import extract_phrases_from_chunks


# ============================================================================
# 정상 케이스 테스트
# ============================================================================

@pytest.mark.asyncio
async def test_extract_phrases_from_chunks_success(
    skip_if_vllm_unavailable,
    sample_chunk_texts,
    sample_video_id
):
    """정상적인 청크 텍스트로 숙어 추출 시 성공 응답 테스트
    
    테스트 대상:
        - app/services/llm/extract_phrases.py의 extract_phrases_from_chunks 함수
        - 여러 청크를 병렬로 처리하여 숙어 추출
        
    검증 내용:
        - 응답에 videoId 필드 포함
        - 응답에 result 필드 포함 (딕셔너리)
        - result에 숙어들이 포함되어 있음
        - 각 숙어의 뜻이 문자열 또는 리스트
    """
    # Arrange (준비): fixture에서 샘플 데이터 가져오기
    chunk_texts = sample_chunk_texts
    video_id = sample_video_id
    
    # Act (실행): 숙어 추출 함수 호출
    result = await extract_phrases_from_chunks(chunk_texts, video_id)
    
    # Assert (검증): 결과 확인
    assert result is not None
    assert isinstance(result, dict)
    assert "videoId" in result
    assert result["videoId"] == video_id
    assert "result" in result
    assert isinstance(result["result"], dict)
    
    # 숙어가 추출되었는지 확인 (숙어가 없을 수도 있음)
    phrases = result["result"]
    assert isinstance(phrases, dict)
    
    # 숙어가 있는 경우 구조 확인
    if len(phrases) > 0:
        sample_phrase = list(phrases.items())[0]
        phrase_key, phrase_meaning = sample_phrase
        
        # 숙어 키는 문자열이어야 함
        assert isinstance(phrase_key, str)
        assert len(phrase_key) > 0
        
        # 숙어는 두 단어 이상이어야 함 (공백 포함)
        words = phrase_key.split()
        assert len(words) >= 2, f"숙어는 두 단어 이상이어야 합니다: {phrase_key}"
        
        # 뜻은 문자열 또는 리스트여야 함
        assert isinstance(phrase_meaning, (str, list))
        if isinstance(phrase_meaning, str):
            assert len(phrase_meaning) > 0
        elif isinstance(phrase_meaning, list):
            assert len(phrase_meaning) > 0
            for meaning in phrase_meaning:
                assert isinstance(meaning, str)
                assert len(meaning) > 0


@pytest.mark.asyncio
async def test_extract_phrases_from_chunks_empty_chunks(
    skip_if_vllm_unavailable,
    sample_video_id
):
    """빈 청크 리스트로 숙어 추출 시 빈 결과 반환 테스트
    
    테스트 대상:
        - 빈 청크 리스트 처리
        
    검증 내용:
        - 응답 구조는 올바르지만 result가 빈 딕셔너리
    """
    # Arrange (준비): 빈 청크 리스트
    chunk_texts = []
    video_id = sample_video_id
    
    # Act (실행): 숙어 추출 함수 호출
    result = await extract_phrases_from_chunks(chunk_texts, video_id)
    
    # Assert (검증): 빈 결과 확인
    assert result is not None
    assert isinstance(result, dict)
    assert "videoId" in result
    assert result["videoId"] == video_id
    assert "result" in result
    assert isinstance(result["result"], dict)
    assert len(result["result"]) == 0


@pytest.mark.asyncio
async def test_extract_phrases_from_chunks_single_chunk(
    skip_if_vllm_unavailable,
    sample_video_id
):
    """단일 청크로 숙어 추출 시 성공 응답 테스트
    
    테스트 대상:
        - 단일 청크 처리
        
    검증 내용:
        - 단일 청크도 정상적으로 처리됨
    """
    # Arrange (준비): 숙어가 포함된 단일 청크
    chunk_texts = [
        "We need to break the ice and start discussing these important topics."
    ]
    video_id = sample_video_id
    
    # Act (실행): 숙어 추출 함수 호출
    result = await extract_phrases_from_chunks(chunk_texts, video_id)
    
    # Assert (검증): 결과 확인
    assert result is not None
    assert isinstance(result, dict)
    assert "videoId" in result
    assert result["videoId"] == video_id
    assert "result" in result
    assert isinstance(result["result"], dict)


# ============================================================================
# 결과 구조 검증 테스트
# ============================================================================

@pytest.mark.asyncio
async def test_extract_phrases_result_structure(
    skip_if_vllm_unavailable,
    sample_chunk_texts,
    sample_video_id
):
    """숙어 추출 결과 구조 검증 테스트
    
    테스트 대상:
        - 결과 딕셔너리의 구조가 올바른지 확인
        
    검증 내용:
        - 모든 숙어가 두 단어 이상
        - 뜻은 문자열 또는 리스트
    """
    # Arrange (준비)
    chunk_texts = sample_chunk_texts
    video_id = sample_video_id
    
    # Act (실행)
    result = await extract_phrases_from_chunks(chunk_texts, video_id)
    
    # Assert (검증): 결과 구조 확인
    phrases = result["result"]
    
    for phrase, meaning in phrases.items():
        # 숙어 키 검증
        assert isinstance(phrase, str)
        assert len(phrase) > 0
        
        # 숙어는 두 단어 이상이어야 함
        words = phrase.split()
        assert len(words) >= 2, f"숙어는 두 단어 이상이어야 합니다: {phrase}"
        
        # 뜻 검증
        assert isinstance(meaning, (str, list))
        if isinstance(meaning, str):
            assert len(meaning) > 0
        elif isinstance(meaning, list):
            assert len(meaning) > 0
            for m in meaning:
                assert isinstance(m, str)
                assert len(m) > 0
    
    # 결과 출력 (테스트 확인용)
    print("\n" + "="*80)
    print(f"[숙어 추출 결과] 총 {len(phrases)}개 숙어 추출됨")
    print("="*80)
    
    if len(phrases) > 0:
        # 처음 5개와 마지막 5개 숙어 출력
        phrase_items = list(phrases.items())
        print("\n[처음 5개 숙어]")
        for i, (phrase, meaning) in enumerate(phrase_items[:5], 1):
            meaning_str = meaning if isinstance(meaning, str) else ", ".join(meaning) if isinstance(meaning, list) else str(meaning)
            print(f"  {i}. {phrase}: {meaning_str}")
        
        if len(phrase_items) > 10:
            print("\n... (중간 생략) ...\n")
        
        print("\n[마지막 5개 숙어]")
        for i, (phrase, meaning) in enumerate(phrase_items[-5:], len(phrase_items) - 4):
            meaning_str = meaning if isinstance(meaning, str) else ", ".join(meaning) if isinstance(meaning, list) else str(meaning)
            print(f"  {i}. {phrase}: {meaning_str}")
        
        # 마지막 숙어 상세 출력
        if phrase_items:
            last_phrase, last_meaning = phrase_items[-1]
            print(f"\n[마지막 숙어 상세]")
            print(f"  숙어: {last_phrase}")
            print(f"  뜻: {last_meaning}")
            print(f"  전체 데이터: {last_meaning}")
    else:
        print("\n[알림] 추출된 숙어가 없습니다.")
    print("="*80 + "\n")

