"""
LLM 프롬프트 템플릿 모듈

단어 추출, 숙어 추출, 상세 정보 생성 등의 프롬프트 템플릿을 관리합니다.
"""
from typing import Dict, List


def get_word_extraction_prompt(chunk_text: str, video_id: str) -> str:
    """
    1단계: 단어 추출 프롬프트
    
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
1. 텍스트에 등장하는 영어 단어 중 **중요 단어(의미가 있는 content word)
    - 포함: 명사, 동사, 형용사, 부사
    - 제외: 관사(a, an, the), 전치사(in, on, at, to 등), 접속사(and, but 등), 대명사(we, you 등), 조동사
2. 각 단어에 대해 문맥상 자연스러운 한국어 뜻을 1~2개 반드시 제공합니다
    - **반드시 한글로만 작성해야 합니다. 한자(중국어)나 다른 언어는 절대 사용하지 마세요.**
    - 예: "인공의", "지능" (올바른 예)
    - 예: "人造的", "智能" (잘못된 예 - 한자 사용 금지)
3. 의미가 없을 경우 절대 "..." 또는 빈 문자열을 넣지 않습니다.
4. 반드시 실제 한국어(한글) 의미만 출력해야 하며 영어, 한자, 중국어 등 다른 언어는 포함되면 안 됩니다
5. 결과는 반드시 다음 JSON 형식으로만 출력합니다:

{{
  "videoId": "{video_id}",
  "result": {{
    "단어1": ["뜻1", "뜻2"],
    "단어2": ["뜻1"],
    "단어3": ["뜻1", "뜻2"]
  }}
}}

중요:
- 반드시 유효한 JSON만 출력하세요.
- JSON 외의 텍스트는 절대 포함하지 마세요.
- 단어는 소문자로 정규화해서 사용하세요.
- "..." 를 출력하는 것은 금지입니다.
- 의미가 불명확하면 문맥 기반으로 가장 자연스러운 한국어 뜻을 제공하세요.
- **단어의 뜻은 반드시 한글로만 작성하세요. 한자(중국어), 영어, 기타 언어는 절대 사용하지 마세요.**
"""


def get_phrase_extraction_prompt(chunk_text: str, video_id: str) -> str:
    """
    1단계: 숙어 추출 프롬프트
    
    Args:
        chunk_text: 자막 청크 텍스트
        video_id: 비디오 ID
        
    Returns:
        프롬프트 문자열
    """
    return f"""
다음은 유튜브 영상의 자막 텍스트입니다. 이 텍스트에서 등장하는 영어 숙어(idiom, phrasal verb, collocation)를 추출하고, 각 숙어에 대해 문맥상 사용되는 한국어 뜻을 제공해주세요.

텍스트:
{chunk_text}

요구사항:
1. 텍스트에 등장하는 숙어를 추출합니다. 숙어는 다음을 포함합니다:
    - Idiom (관용구): 예) "break the ice", "once in a blue moon"
    - Phrasal verb (구동사): 예) "give up", "look forward to"
    - Collocation (연어): 예) "make a decision", "take a break"
2. 각 숙어에 대해 문맥상 사용되는 한국어 뜻을 제공합니다.
    - **반드시 한글로만 작성해야 합니다. 한자(중국어)나 다른 언어는 절대 사용하지 마세요.**
    - 예: "깊이 파고들다", "혁신시키다" (올바른 예)
    - 예: "深入", "革新" (잘못된 예 - 한자 사용 금지)
3. 결과는 반드시 다음 JSON 형식으로 반환해야 합니다:

{{
  "videoId": "{video_id}",
  "result": {{
    "숙어1": "뜻1",
    "숙어2": "뜻2",
    "숙어3": "뜻3"
  }}
}}

중요:
- 반드시 유효한 JSON 형식으로만 응답하세요.
- 다른 설명이나 텍스트는 포함하지 마세요.
- 일반적인 단어 조합은 제외하고, 의미가 특별한 숙어만 추출하세요.
- **숙어의 뜻은 반드시 한글로만 작성하세요. 한자(중국어), 영어, 기타 언어는 절대 사용하지 마세요.**
"""


def get_word_enrichment_prompt(
    words: Dict[str, List[str]], 
    chunk_text: str, 
    video_id: str
) -> str:
    """
    2단계: 단어 상세 정보 생성 프롬프트 (품사, 동의어, 예문)
    
    Args:
        words: 단어와 뜻 딕셔너리 (예: {"word": ["뜻1", "뜻2"]})
        chunk_text: 원본 청크 텍스트
        video_id: 비디오 ID
        
    Returns:
        프롬프트 문자열
    """
    words_str = "\n".join([f"- {word}: {', '.join(meanings)}" for word, meanings in words.items()])
    
    return f"""
다음 단어들에 대해 품사, 동의어(최대 2개), 그리고 예문을 생성해주세요.

원본 텍스트:
{chunk_text}

단어 목록:
{words_str}

요구사항:
1. 각 단어에 대해 품사를 영어 약어로만 제공합니다.
   - 명사: "n"
   - 동사: "v"
   - 형용사: "adj"
   - 부사: "adv"
   - 기타 품사도 영어 약어만 표기 (예: "pron", "intj", "prep" 등)
   - **중요: 품사 값은 영어 약어만 사용하고, 괄호나 설명을 절대 추가하지 마세요.**
   - 예: "품사": "n" (올바른 예)
   - 예: "품사": "n (noun)" (잘못된 예 - 괄호와 설명 포함 금지)
   - 예: "품사": "intj" (올바른 예)
   - 예: "품사": "intj (interjection)" (잘못된 예 - 괄호와 설명 포함 금지)
2. 각 단어에 대해 영어 동의어(synonym)를 최대 2개까지 제공합니다.
   - 동의어는 반드시 영어 단어로 제공해야 합니다.
   - 한글 뜻이 아닌 영어 단어를 제공하세요.
3. 각 단어에 대해 원본 텍스트의 문맥을 고려한 영어 예문을 제공합니다.
   - 예문은 반드시 영어로 작성해야 합니다.
   - 한글이 아닌 영어 문장으로 작성하세요.
4. 결과는 반드시 다음 JSON 형식으로 반환해야 합니다:

{{
  "videoId": "{video_id}",
  "result": {{
    "단어1": {{
      "품사": "n",
      "동의어": ["synonym1", "synonym2"],
      "예문": "Example sentence in English."
    }},
    "단어2": {{
      "품사": "v",
      "동의어": ["synonym1"],
      "예문": "Example sentence in English."
    }}
  }}
}}

중요:
- 반드시 유효한 JSON 형식으로만 응답하세요.
- 다른 설명이나 텍스트는 포함하지 마세요.
- 품사는 영어 약어(n, v, adj, adv, pron, intj 등)만 사용하고, 괄호나 설명을 절대 추가하지 마세요.
- 동의어는 반드시 영어 단어로 제공하세요.
- 예문은 반드시 영어로 작성하세요.
- 예문은 원본 텍스트의 문맥을 반영하여 작성하세요.
- JSON 형식이 유효하지 않으면 파싱이 실패하므로, 반드시 유효한 JSON만 출력하세요.
"""


def get_phrase_enrichment_prompt(
    phrases: Dict[str, str],
    chunk_text: str,
    video_id: str
) -> str:
    """
    2단계: 숙어 예문 생성 프롬프트
    
    Args:
        phrases: 숙어와 뜻 딕셔너리 (예: {"phrase": "뜻"})
        chunk_text: 원본 청크 텍스트
        video_id: 비디오 ID
        
    Returns:
        프롬프트 문자열
    """
    phrases_str = "\n".join([f"- {phrase}: {meaning}" for phrase, meaning in phrases.items()])
    
    return f"""다음 숙어들에 대해 원본 텍스트의 문맥을 고려한 영어 예문을 생성해주세요.

원본 텍스트:
{chunk_text}

숙어 목록:
{phrases_str}

요구사항:
1. 각 숙어에 대해 원본 텍스트의 문맥을 고려한 영어 예문을 제공합니다.
   - 예문은 반드시 영어로 작성해야 합니다.
   - 한글이 아닌 영어 문장으로 작성하세요.
   - 해당 숙어를 사용한 자연스러운 영어 예문을 작성하세요.
2. 결과는 반드시 다음 JSON 형식으로 반환해야 합니다:

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
- 반드시 유효한 JSON 형식으로만 응답하세요.
- 다른 설명이나 텍스트는 포함하지 마세요.
- 예문은 반드시 영어로 작성하세요.
- 예문은 원본 텍스트의 문맥을 반영하여 작성하세요.
- 해당 숙어를 사용한 자연스러운 영어 예문을 작성하세요."""

