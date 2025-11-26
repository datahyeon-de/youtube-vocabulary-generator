"""
LLM 프롬프트 템플릿 모듈

단어 추출, 숙어 추출, 상세 정보 생성 등의 프롬프트 템플릿을 관리합니다.
"""
from typing import Dict, List, Any


def get_word_extraction_prompt(chunk_text: str, video_id: str) -> str:
    """
    1단계: 단어 추출 프롬프트 (v10 기반)
    
    Args:
        chunk_text: 자막 청크 텍스트
        video_id: 비디오 ID
        
    Returns:
        프롬프트 문자열
    """
    return f"""
다음은 유튜브 영상의 자막 텍스트입니다. 이 텍스트에서 등장하는 모든 영어 단어를 추출하고, 각 단어에 대해 문맥상 사용되는 한국어 뜻을 최대 2개까지 제공해주세요.

텍스트:
{chunk_text}

요구사항:
1. 각 단어에 대해 문맥상 자연스러운 뜻을 "한국어"로 1~2개 반드시 제공합니다.
2. 텍스트에 등장하는 단어는 "영어사전에 등록된 단어"의 "원형"과 "품사"를 추출하는 것을 원칙으로 합니다.
3. 단어의 추출 기준: 명사, 동사, 형용사, 부사만 포함. 관사, 전치사, 접속사, 대명사, 조동사, 감탄사는 제외.
4. 품사 표시: "n"(명사), "v"(동사), "adj"(형용사), "adv"(부사)만 사용.
5. 각 단어에 대해: 원형 기준으로만 표기, 뜻은 최대 2개, 의미가 겹치면 하나만 유지.
6. 단어 뜻이 불명할 경우 문맥 기반으로 가장 비슷한 사전적 의미의 "한국어 뜻"을 제공합니다.

중요:
- 단어의 뜻에 "..." 및 "중국어", "한자"의 사용을 금지합니다.
- 단어의 뜻에 "masc.:", "female:", "남성:", "여성:" 등 성별 구분 표기를 절대 사용하지 마세요.
- 단어는 반드시 소문자로 정규화해서 사용하세요.
- 같은 의미가 반복되거나 동일 의미를 표현하는 문장을 두 번 작성하지 마세요.

결과는 반드시 다음 JSON 형식으로만 출력합니다:

{{
  "videoId": "{video_id}",
  "result": {{
    "단어1": {{"품사": "n", "뜻": ["뜻1", "뜻2"]}},
    "단어2": {{"품사": "v", "뜻": ["뜻1"]}}
  }}
}}

중요:
- 마크다운 코드 블록(```json 또는 ```)을 절대 사용하지 마세요. 순수 JSON만 출력하세요.
- JSON 외의 텍스트는 절대 포함하지 마세요.
- JSON 형식이 유효하지 않으면 파싱이 실패하므로, 반드시 유효한 JSON만 출력하세요.
"""


def get_phrase_extraction_prompt(chunk_text: str, video_id: str) -> str:
    """
    1단계: 숙어 추출 프롬프트 (v1 기반)
    
    Args:
        chunk_text: 자막 청크 텍스트
        video_id: 비디오 ID
        
    Returns:
        프롬프트 문자열
    """
    return f"""
결과는 반드시 다음 JSON 형식으로만 출력합니다:

{{
  "videoId": "{video_id}",
  "result": {{
    "숙어1": "뜻1",
    "숙어2": "뜻2",
    "숙어3": "뜻3"
  }}
}}

⚠️ 중요: 마크다운 코드 블록(```json 또는 ```)을 절대 사용하지 마세요. 순수 JSON만 출력하세요.
⚠️ 중요: JSON 외의 텍스트는 절대 포함하지 마세요.

다음은 유튜브 영상의 자막 텍스트입니다. 이 텍스트에서 등장하는 영어 숙어(idiom, phrasal verb, collocation)를 추출하고, 각 숙어에 대해 문맥상 사용되는 한국어 뜻을 제공해주세요.

텍스트:
{chunk_text}

요구사항:
1. 텍스트에 등장하는 숙어를 추출합니다. 숙어는 다음을 포함합니다:
   - Idiom (관용구): 예) "break the ice", "once in a blue moon"
   - Phrasal verb (구동사): 예) "give up", "look forward to"
   - Collocation (연어): 예) "make a decision", "take a break"
2. 두 단어 이상으로 이루어진 표현만 숙어로 인정합니다. 단일 단어나 단순 명사/동사는 절대로 포함하지 마세요.
3. 숙어는 문맥상 특별한 의미 또는 관용적 의미가 드러나는 표현만 선택합니다. 단순히 빈출하는 일반 조합은 제외합니다.
4. 각 숙어에 대한 뜻은 문맥상 자연스러운 "한국어"로 제공합니다.

⚠️ 중요: 일반적인 단어 조합은 제외하고, 의미가 특별한 숙어만 추출하세요.
⚠️ 중요: 단일 단어이거나 공백이 없는 표현은 무조건 제외하고, 최소 두 개 이상의 토큰을 가진 표현만 작성하세요.
⚠️ 중요: 숙어의 뜻에 "..." 및 "중국어", "한자"의 사용을 금지합니다.
"""


def get_word_enrichment_prompt_v1(
    words: Dict[str, Dict[str, Any]], 
    video_id: str
) -> str:
    """
    2단계: 단어 상세 정보 생성 프롬프트 v1 (출력 형식 앞에 배치, 강한 강조)
    
    Args:
        words: 1단계 단어 추출 결과 딕셔너리 (예: {"word": {"품사": "n", "뜻": ["뜻1", "뜻2"]}})
        video_id: 비디오 ID
        
    Returns:
        프롬프트 문자열
    """
    # 1단계 결과 포맷에서 단어와 뜻만 추출하여 표시
    words_str = "\n".join([
        f"- {word}: {', '.join(word_data.get('뜻', []))} (품사: {word_data.get('품사', 'N/A')})"
        for word, word_data in words.items()
        if isinstance(word_data, dict)
    ])
    
    return f"""
결과는 반드시 다음 JSON 형식으로만 출력합니다:

{{
  "videoId": "{video_id}",
  "result": {{
    "단어1": {{
      "동의어": ["synonym1", "synonym2"],
      "예문": "Example sentence in English."
    }},
    "단어2": {{
      "동의어": ["synonym1"],
      "예문": "Example sentence in English."
    }}
  }}
}}

⚠️ 중요: 마크다운 코드 블록(```json 또는 ```)을 절대 사용하지 마세요. 순수 JSON만 출력하세요.
⚠️ 중요: JSON 외의 텍스트는 절대 포함하지 마세요.

다음 단어들에 대해 영어 동의어(최대 2개)와 예문을 생성해주세요.

단어 목록:
{words_str}

요구사항:
1. 각 단어에 대해 영어 동의어(synonym)를 "최대 2개까지" 제공합니다.
2. 각 단어에 대해 해당 단어를 사용한 간단한 영어 예문을 "반드시 1개" 제공합니다.
3. 동의어와 예문은 반드시 영어로 작성해야 합니다.
"""


def get_word_enrichment_prompt_v7(
    words: Dict[str, Dict[str, Any]], 
    video_id: str
) -> str:
    """
    2단계: 단어 상세 정보 생성 프롬프트 v7 (출력 형식 뒤에 배치, 간결한 강조)
    
    Args:
        words: 1단계 단어 추출 결과 딕셔너리 (예: {"word": {"품사": "n", "뜻": ["뜻1", "뜻2"]}})
        video_id: 비디오 ID
        
    Returns:
        프롬프트 문자열
    """
    # 1단계 결과 포맷에서 단어와 뜻만 추출하여 표시
    words_str = "\n".join([
        f"- {word}: {', '.join(word_data.get('뜻', []))} (품사: {word_data.get('품사', 'N/A')})"
        for word, word_data in words.items()
        if isinstance(word_data, dict)
    ])
    
    return f"""
다음 단어들에 대해 영어 동의어(최대 2개)와 예문을 생성해주세요.

단어 목록:
{words_str}

요구사항:
1. 각 단어에 대해 영어 동의어(synonym)를 "최대 2개까지" 제공합니다.
2. 각 단어에 대해 해당 단어를 사용한 간단한 영어 예문을 "반드시 1개" 제공합니다.
3. 동의어와 예문은 반드시 영어로 작성해야 합니다.

결과는 반드시 다음 JSON 형식으로만 출력합니다:

{{
  "videoId": "{video_id}",
  "result": {{
    "단어1": {{
      "동의어": ["synonym1", "synonym2"],
      "예문": "Example sentence in English."
    }},
    "단어2": {{
      "동의어": ["synonym1"],
      "예문": "Example sentence in English."
    }}
  }}
}}

중요:
- 마크다운 코드 블록(```json 또는 ```)을 절대 사용하지 마세요. 순수 JSON만 출력하세요.
- JSON 외의 텍스트는 절대 포함하지 마세요.
- 동의어와 예문은 반드시 영어로 작성해야 합니다.
- JSON 형식이 유효하지 않으면 파싱이 실패하므로, 반드시 유효한 JSON만 출력하세요.
"""


def get_word_enrichment_prompt(
    words: Dict[str, Dict[str, Any]], 
    video_id: str,
    version: str = "v1"
) -> str:
    """
    2단계: 단어 상세 정보 생성 프롬프트 (기본값: v1)
    
    Args:
        words: 1단계 단어 추출 결과 딕셔너리 (예: {"word": {"품사": "n", "뜻": ["뜻1", "뜻2"]}})
        video_id: 비디오 ID
        version: 프롬프트 버전 ("v1" 또는 "v7")
        
    Returns:
        프롬프트 문자열
    """
    if version == "v7":
        return get_word_enrichment_prompt_v7(words, video_id)
    else:
        return get_word_enrichment_prompt_v1(words, video_id)


def get_phrase_enrichment_prompt_v1(
    phrases: Dict[str, str],
    video_id: str
) -> str:
    """
    2단계: 숙어 예문 생성 프롬프트 v1 (출력 형식 앞에 배치, 강한 강조)
    
    Args:
        phrases: 숙어와 뜻 딕셔너리 (예: {"phrase": "뜻"})
        video_id: 비디오 ID
        
    Returns:
        프롬프트 문자열
    """
    phrases_str = "\n".join([f"- {phrase}: {meaning}" for phrase, meaning in phrases.items()])
    
    return f"""
결과는 반드시 다음 JSON 형식으로만 출력합니다:

{{
  "videoId": "{video_id}",
  "result": {{
    "숙어1": {{
      "예문": "Example sentence in English using the phrase."
    }},
    "숙어2": {{
      "예문": "Example sentence in English using the phrase."
    }}
  }}
}}

⚠️ 중요: 마크다운 코드 블록(```json 또는 ```)을 절대 사용하지 마세요. 순수 JSON만 출력하세요.
⚠️ 중요: JSON 외의 텍스트는 절대 포함하지 마세요.

다음 숙어들에 대해 해당 숙어를 사용한 간단한 영어 예문을 생성해주세요.

숙어 목록:
{phrases_str}

요구사항:
1. 각 숙어에 대해 해당 숙어를 사용한 간단한 영어 예문을 "반드시 1개" 제공합니다.
2. 예문은 반드시 영어로 작성해야 합니다.
"""


def get_phrase_enrichment_prompt_v7(
    phrases: Dict[str, str],
    video_id: str
) -> str:
    """
    2단계: 숙어 예문 생성 프롬프트 v7 (출력 형식 뒤에 배치, 간결한 강조)
    
    Args:
        phrases: 숙어와 뜻 딕셔너리 (예: {"phrase": "뜻"})
        video_id: 비디오 ID
        
    Returns:
        프롬프트 문자열
    """
    phrases_str = "\n".join([f"- {phrase}: {meaning}" for phrase, meaning in phrases.items()])
    
    return f"""
다음 숙어들에 대해 해당 숙어를 사용한 간단한 영어 예문을 생성해주세요.

숙어 목록:
{phrases_str}

요구사항:
1. 각 숙어에 대해 해당 숙어를 사용한 간단한 영어 예문을 "반드시 1개" 제공합니다.
2. 예문은 반드시 영어로 작성해야 합니다.

결과는 반드시 다음 JSON 형식으로만 출력합니다:

{{
  "videoId": "{video_id}",
  "result": {{
    "숙어1": {{
      "예문": "Example sentence in English using the phrase."
    }},
    "숙어2": {{
      "예문": "Example sentence in English using the phrase."
    }}
  }}
}}

중요:
- 마크다운 코드 블록(```json 또는 ```)을 절대 사용하지 마세요. 순수 JSON만 출력하세요.
- JSON 외의 텍스트는 절대 포함하지 마세요.
- 예문은 반드시 영어로 작성해야 합니다.
- JSON 형식이 유효하지 않으면 파싱이 실패하므로, 반드시 유효한 JSON만 출력하세요.
"""


def get_phrase_enrichment_prompt(
    phrases: Dict[str, str],
    video_id: str,
    version: str = "v1"
) -> str:
    """
    2단계: 숙어 예문 생성 프롬프트 (기본값: v1)
    
    Args:
        phrases: 숙어와 뜻 딕셔너리 (예: {"phrase": "뜻"})
        video_id: 비디오 ID
        version: 프롬프트 버전 ("v1" 또는 "v7")
        
    Returns:
        프롬프트 문자열
    """
    if version == "v7":
        return get_phrase_enrichment_prompt_v7(phrases, video_id)
    else:
        return get_phrase_enrichment_prompt_v1(phrases, video_id)

