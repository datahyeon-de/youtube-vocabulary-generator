"""
프롬프트 A/B 테스트 모듈

1단계와 2단계 프롬프트의 여러 버전을 A/B 테스트하여 최적의 프롬프트 버전을 찾습니다.
"""
import asyncio
import json
import pytest
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

from app.services.llm.client import VLLMClient

# 프롬프트 함수들을 tests/test_services/test_llm_prompt_ab_test_prompts.py에서 import
from tests.test_services.test_llm_prompt_ab_test_prompts import (
    get_word_extraction_prompt_v1,
    get_word_extraction_prompt_v2,
    get_word_extraction_prompt_v3,
    get_word_extraction_prompt_v4,
    get_word_extraction_prompt_v5,
    get_word_extraction_prompt_v6,
    get_word_extraction_prompt_v7,
    get_word_extraction_prompt_v8,
    get_word_extraction_prompt_v9,
    get_word_extraction_prompt_v10,
    get_phrase_extraction_prompt_v1,
    get_phrase_extraction_prompt_v2,
    get_phrase_extraction_prompt_v3,
    get_phrase_extraction_prompt_v4,
    get_phrase_extraction_prompt_v5,
    get_phrase_extraction_prompt_v6,
    get_phrase_extraction_prompt_v7,
    get_phrase_extraction_prompt_v8,
    get_phrase_extraction_prompt_v9,
    get_phrase_extraction_prompt_v10,
    get_word_enrichment_prompt_v1,
    get_word_enrichment_prompt_v2,
    get_word_enrichment_prompt_v3,
    get_word_enrichment_prompt_v4,
    get_word_enrichment_prompt_v5,
    get_word_enrichment_prompt_v6,
    get_word_enrichment_prompt_v7,
    get_word_enrichment_prompt_v8,
    get_word_enrichment_prompt_v9,
    get_word_enrichment_prompt_v10,
    get_phrase_enrichment_prompt_v1,
    get_phrase_enrichment_prompt_v2,
    get_phrase_enrichment_prompt_v3,
    get_phrase_enrichment_prompt_v4,
    get_phrase_enrichment_prompt_v5,
    get_phrase_enrichment_prompt_v6,
    get_phrase_enrichment_prompt_v7,
    get_phrase_enrichment_prompt_v8,
    get_phrase_enrichment_prompt_v9,
    get_phrase_enrichment_prompt_v10,
)


# ============================================================================
# 헬퍼 함수
# ============================================================================

async def test_single_run(
    prompt: str,
    run_num: int,
    client: VLLMClient
) -> Dict[str, Any]:
    """단일 테스트 실행"""
    try:
        # LLM API 호출
        messages = [{"role": "user", "content": prompt}]
        response = await client.chat_completion(messages, temperature=0.7)
        
        # 응답에서 콘텐츠 추출
        content = await client.extract_content_from_response(response)
        
        # JSON 파싱 시도
        try:
            parsed = json.loads(content)
            
            # 기본 구조 검증
            if "videoId" in parsed and "result" in parsed:
                return {
                    "run": run_num,
                    "success": True,
                    "content_preview": content[:200] + "..." if len(content) > 200 else content
                }
            else:
                return {
                    "run": run_num,
                    "success": False,
                    "error": "Invalid structure",
                    "content": content  # 전체 내용 저장
                }
        except json.JSONDecodeError as e:
            return {
                "run": run_num,
                "success": False,
                "error": f"JSON Parse Error: {str(e)}",
                "content": content  # 전체 내용 저장
            }
    except Exception as e:
        return {
            "run": run_num,
            "success": False,
            "error": f"Exception: {str(e)}",
            "content": ""
        }


async def test_prompt_version(
    prompt_func,
    version_num: int,
    test_type: str,
    chunk_text: str = None,
    video_id: str = None,
    words: Dict[str, Dict[str, Any]] = None,
    phrases: Dict[str, str] = None,
    num_runs: int = 10
) -> Dict[str, Any]:
    """특정 프롬프트 버전을 여러 번 테스트 (병렬 처리)"""
    results = {
        "version": version_num,
        "test_type": test_type,
        "total_runs": num_runs,
        "success_count": 0,
        "failure_count": 0,
        "errors": [],
        "success_samples": [],
        "failure_samples": []
    }
    
    # 프롬프트 생성 (한 번만)
    if test_type in ["word_enrichment"]:
        prompt = prompt_func(words, video_id)
    elif test_type in ["phrase_enrichment"]:
        prompt = prompt_func(phrases, video_id)
    else:
        prompt = prompt_func(chunk_text, video_id)
    
    # 비동기로 10번 동시 실행
    async with VLLMClient() as client:
        tasks = [
            test_single_run(prompt, run_num, client)
            for run_num in range(1, num_runs + 1)
        ]
        run_results = await asyncio.gather(*tasks)
    
    # 결과 집계
    for run_result in run_results:
        if run_result["success"]:
            results["success_count"] += 1
            if len(results["success_samples"]) < 3:
                results["success_samples"].append({
                    "run": run_result["run"],
                    "content_preview": run_result.get("content_preview", "")
                })
        else:
            results["failure_count"] += 1
            # 실패한 경우 전체 content 저장
            full_content = run_result.get("content", "")
            results["errors"].append({
                "run": run_result["run"],
                "error": run_result.get("error", "Unknown error"),
                "content": full_content  # 전체 내용 저장
            })
            # 모든 실패 케이스 저장 (제한 없음)
            results["failure_samples"].append({
                "run": run_result["run"],
                "error": run_result.get("error", "Unknown error"),
                "content": full_content  # 전체 내용 저장
            })
    
    results["success_rate"] = (results["success_count"] / num_runs) * 100
    return results


# ============================================================================
# 1단계 통합 테스트 함수
# ============================================================================

async def _test_stage1_word_extraction(
    output_file: Path, 
    all_results: List[Dict[str, Any]],
    chunk_text: str,
    video_id: str
):
    """1단계: 단어 추출 프롬프트 A/B 테스트"""
    word_prompt_funcs = [
        get_word_extraction_prompt_v1,
        get_word_extraction_prompt_v2,
        get_word_extraction_prompt_v3,
        get_word_extraction_prompt_v4,
        get_word_extraction_prompt_v5,
        get_word_extraction_prompt_v6,
        get_word_extraction_prompt_v7,
        get_word_extraction_prompt_v8,
        get_word_extraction_prompt_v9,
        get_word_extraction_prompt_v10,
    ]
    
    print(f"\n[단어 추출 프롬프트 테스트 시작]")
    print(f"테스트 청크 길이: {len(chunk_text)} 문자\n")
    
    for i, prompt_func in enumerate(word_prompt_funcs, 1):
        print(f"단어 추출 버전 {i}/10 테스트 중...", end=" ", flush=True)
        result = await test_prompt_version(
            prompt_func, i, "word_extraction",
            chunk_text, video_id, num_runs=10
        )
        all_results.append(result)
        print(f"완료 (성공률: {result['success_rate']:.1f}%)")
        
        # 즉시 파일에 저장
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)
        
        # 즉시 출력
        print(f"  -> 성공 {result['success_count']}/10, 실패 {result['failure_count']}/10")
        if result['failure_count'] > 0:
            print(f"  -> 실패 원인: {result['errors'][0]['error'] if result['errors'] else 'Unknown'}")


async def _test_stage1_phrase_extraction(
    output_file: Path, 
    all_results: List[Dict[str, Any]],
    chunk_text: str,
    video_id: str
):
    """1단계: 숙어 추출 프롬프트 A/B 테스트"""
    phrase_prompt_funcs = [
        get_phrase_extraction_prompt_v1,
        get_phrase_extraction_prompt_v2,
        get_phrase_extraction_prompt_v3,
        get_phrase_extraction_prompt_v4,
        get_phrase_extraction_prompt_v5,
        get_phrase_extraction_prompt_v6,
        get_phrase_extraction_prompt_v7,
        get_phrase_extraction_prompt_v8,
        get_phrase_extraction_prompt_v9,
        get_phrase_extraction_prompt_v10,
    ]
    
    print(f"\n[숙어 추출 프롬프트 테스트 시작]")
    print(f"테스트 청크 길이: {len(chunk_text)} 문자\n")
    
    for i, prompt_func in enumerate(phrase_prompt_funcs, 1):
        print(f"숙어 추출 버전 {i}/10 테스트 중...", end=" ", flush=True)
        result = await test_prompt_version(
            prompt_func, i, "phrase_extraction",
            chunk_text, video_id, num_runs=10
        )
        all_results.append(result)
        print(f"완료 (성공률: {result['success_rate']:.1f}%)")
        
        # 즉시 파일에 저장
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)
        
        # 즉시 출력
        print(f"  -> 성공 {result['success_count']}/10, 실패 {result['failure_count']}/10")
        if result['failure_count'] > 0:
            print(f"  -> 실패 원인: {result['errors'][0]['error'] if result['errors'] else 'Unknown'}")


# ============================================================================
# 2단계 통합 테스트 함수
# ============================================================================

async def _test_stage2_word_enrichment(
    output_file: Path, 
    all_results: List[Dict[str, Any]],
    word_extraction_result: Dict[str, Any],
    video_id: str
):
    """2단계: 단어 상세 정보 생성 프롬프트 A/B 테스트"""
    word_enrichment_prompt_funcs = [
        get_word_enrichment_prompt_v1,
        get_word_enrichment_prompt_v2,
        get_word_enrichment_prompt_v3,
        get_word_enrichment_prompt_v4,
        get_word_enrichment_prompt_v5,
        get_word_enrichment_prompt_v6,
        get_word_enrichment_prompt_v7,
        get_word_enrichment_prompt_v8,
        get_word_enrichment_prompt_v9,
        get_word_enrichment_prompt_v10,
    ]
    
    mock_words = word_extraction_result.get("result", {})
    
    print(f"\n[단어 상세 정보 생성 프롬프트 테스트 시작]")
    print(f"테스트 단어 수: {len(mock_words)}개\n")
    
    for i, prompt_func in enumerate(word_enrichment_prompt_funcs, 1):
        print(f"단어 상세 정보 생성 버전 {i}/10 테스트 중...", end=" ", flush=True)
        result = await test_prompt_version(
            prompt_func, i, "word_enrichment",
            video_id=video_id,
            words=mock_words,
            num_runs=10
        )
        all_results.append(result)
        print(f"완료 (성공률: {result['success_rate']:.1f}%)")
        
        # 즉시 파일에 저장
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)
        
        # 즉시 출력
        print(f"  -> 성공 {result['success_count']}/10, 실패 {result['failure_count']}/10")
        if result['failure_count'] > 0:
            print(f"  -> 실패 원인: {result['errors'][0]['error'] if result['errors'] else 'Unknown'}")


async def _test_stage2_phrase_enrichment(
    output_file: Path, 
    all_results: List[Dict[str, Any]],
    phrase_extraction_result: Dict[str, Any],
    video_id: str
):
    """2단계: 숙어 예문 생성 프롬프트 A/B 테스트"""
    phrase_enrichment_prompt_funcs = [
        get_phrase_enrichment_prompt_v1,
        get_phrase_enrichment_prompt_v2,
        get_phrase_enrichment_prompt_v3,
        get_phrase_enrichment_prompt_v4,
        get_phrase_enrichment_prompt_v5,
        get_phrase_enrichment_prompt_v6,
        get_phrase_enrichment_prompt_v7,
        get_phrase_enrichment_prompt_v8,
        get_phrase_enrichment_prompt_v9,
        get_phrase_enrichment_prompt_v10,
    ]
    
    mock_phrases = phrase_extraction_result.get("result", {})
    
    print(f"\n[숙어 예문 생성 프롬프트 테스트 시작]")
    print(f"테스트 숙어 수: {len(mock_phrases)}개\n")
    
    for i, prompt_func in enumerate(phrase_enrichment_prompt_funcs, 1):
        print(f"숙어 예문 생성 버전 {i}/10 테스트 중...", end=" ", flush=True)
        result = await test_prompt_version(
            prompt_func, i, "phrase_enrichment",
            video_id=video_id,
            phrases=mock_phrases,
            num_runs=10
        )
        all_results.append(result)
        print(f"완료 (성공률: {result['success_rate']:.1f}%)")
        
        # 즉시 파일에 저장
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)
        
        # 즉시 출력
        print(f"  -> 성공 {result['success_count']}/10, 실패 {result['failure_count']}/10")
        if result['failure_count'] > 0:
            print(f"  -> 실패 원인: {result['errors'][0]['error'] if result['errors'] else 'Unknown'}")


# ============================================================================
# pytest 테스트 함수
# ============================================================================

@pytest.mark.asyncio
async def test_stage1_prompt_ab_test(
    skip_if_vllm_unavailable,
    ab_test_chunk_text,
    ab_test_video_id
):
    """1단계 프롬프트 A/B 테스트 (단어 추출, 숙어 추출)
    
    테스트 대상:
        - 단어 추출 프롬프트 10개 버전 (각 10번 실행)
        - 숙어 추출 프롬프트 10개 버전 (각 10번 실행)
    
    출력:
        - 테스트 결과 JSON 파일 생성 (tests/test_services/ab_test_results/ab_test_results_stage1_YYYYMMDD_HHMMSS.json)
    """
    print(f"\n{'='*80}")
    print(f"1단계 프롬프트 A/B 테스트 시작 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}\n")
    
    # 결과 파일 디렉토리 생성
    results_dir = Path(__file__).parent / "ab_test_results"
    results_dir.mkdir(exist_ok=True)
    
    # 결과 파일 경로 (타임스탬프 포함)
    output_file = results_dir / f"ab_test_results_stage1_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    all_results = []
    
    # 단어 추출 테스트
    await _test_stage1_word_extraction(output_file, all_results, ab_test_chunk_text, ab_test_video_id)
    
    # 숙어 추출 테스트
    await _test_stage1_phrase_extraction(output_file, all_results, ab_test_chunk_text, ab_test_video_id)
    
    # 최종 결과 출력
    print(f"\n{'='*80}")
    print("1단계 테스트 결과 요약")
    print(f"{'='*80}\n")
    
    word_results = [r for r in all_results if r["test_type"] == "word_extraction"]
    phrase_results = [r for r in all_results if r["test_type"] == "phrase_extraction"]
    
    if word_results:
        print("단어 추출 결과:")
        print("-" * 80)
        for r in sorted(word_results, key=lambda x: x["success_rate"], reverse=True):
            print(f"버전 {r['version']:2d}: 성공 {r['success_count']:2d}/10 ({r['success_rate']:5.1f}%) | 실패 {r['failure_count']:2d}/10")
        print()
    
    if phrase_results:
        print("숙어 추출 결과:")
        print("-" * 80)
        for r in sorted(phrase_results, key=lambda x: x["success_rate"], reverse=True):
            print(f"버전 {r['version']:2d}: 성공 {r['success_count']:2d}/10 ({r['success_rate']:5.1f}%) | 실패 {r['failure_count']:2d}/10")
        print()
    
    print(f"\n결과가 저장되었습니다: {output_file}")
    print(f"{'='*80}\n")


@pytest.mark.asyncio
async def test_stage2_prompt_ab_test(
    skip_if_vllm_unavailable,
    mock_word_extraction_result,
    mock_phrase_extraction_result,
    ab_test_video_id
):
    """2단계 프롬프트 A/B 테스트 (단어 상세 정보 생성, 숙어 예문 생성)
    
    테스트 대상:
        - 단어 상세 정보 생성 프롬프트 10개 버전 (각 10번 실행)
        - 숙어 예문 생성 프롬프트 10개 버전 (각 10번 실행)
    
    출력:
        - 테스트 결과 JSON 파일 생성 (tests/test_services/ab_test_results/ab_test_results_stage2_YYYYMMDD_HHMMSS.json)
    """
    print(f"\n{'='*80}")
    print(f"2단계 프롬프트 A/B 테스트 시작 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}\n")
    
    # 결과 파일 디렉토리 생성
    results_dir = Path(__file__).parent / "ab_test_results"
    results_dir.mkdir(exist_ok=True)
    
    # 결과 파일 경로 (타임스탬프 포함)
    output_file = results_dir / f"ab_test_results_stage2_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    all_results = []
    
    # 단어 상세 정보 생성 테스트
    await _test_stage2_word_enrichment(output_file, all_results, mock_word_extraction_result, ab_test_video_id)
    
    # 숙어 예문 생성 테스트
    await _test_stage2_phrase_enrichment(output_file, all_results, mock_phrase_extraction_result, ab_test_video_id)
    
    # 최종 결과 출력
    print(f"\n{'='*80}")
    print("2단계 테스트 결과 요약")
    print(f"{'='*80}\n")
    
    word_enrichment_results = [r for r in all_results if r["test_type"] == "word_enrichment"]
    phrase_enrichment_results = [r for r in all_results if r["test_type"] == "phrase_enrichment"]
    
    if word_enrichment_results:
        print("단어 상세 정보 생성 결과:")
        print("-" * 80)
        for r in sorted(word_enrichment_results, key=lambda x: x["success_rate"], reverse=True):
            print(f"버전 {r['version']:2d}: 성공 {r['success_count']:2d}/10 ({r['success_rate']:5.1f}%) | 실패 {r['failure_count']:2d}/10")
        print()
    
    if phrase_enrichment_results:
        print("숙어 예문 생성 결과:")
        print("-" * 80)
        for r in sorted(phrase_enrichment_results, key=lambda x: x["success_rate"], reverse=True):
            print(f"버전 {r['version']:2d}: 성공 {r['success_count']:2d}/10 ({r['success_rate']:5.1f}%) | 실패 {r['failure_count']:2d}/10")
        print()
    
    print(f"\n결과가 저장되었습니다: {output_file}")
    print(f"{'='*80}\n")

