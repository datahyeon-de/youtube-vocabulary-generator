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
1. 각 단어에 대해 문맥상 자연스러운 뜻을 "한국어"로 1~2개 반드시 제공합니다.
2. 텍스트에 등장하는 단어는 "영어사전에 등록된 단어"의 "원형"과 "품사"를 추출하는 것을 원칙으로 합니다.
    - 원형 예시1: "cats" -> "cat", "dogs" -> "dog"
    - 원형 예시2: "going" -> "go", "worked" -> "work"
    - 원형 예시3: "slowly" -> "slowly", "quick" -> "quick"
3. 단어의 추출 기준은 품사 아래 항목을 참고하여 추출합니다:    
    - 포함 단어: 명사, 동사, 형용사, 부사
    - 제외 단어: 관사(a, an, the), 전치사(in, on, at, to 등), 접속사(and, but 등), 대명사(we, you 등), 조동사, 감탄사(hello, hi, yeah, well, wow 등)
4. 품사의 표시는 반드시 다음 "영어 약어" 목록에 있는 것만 사용합니다:
    - 명사: "n"
    - 동사: "v"
    - 형용사: "adj"
    - 부사: "adv"
5. 각 단어에 대해 아래 조건을 반드시 따릅니다:
    - **원형 기준**으로만 표기하며, 같은 단어를 중복으로 기재하지 않습니다.
    - "뜻" 리스트는 **최대 2개**까지 작성하고, 의미가 겹치거나 표현만 다른 경우에는 **하나만 유지**합니다.
    - "뜻" 항목마다 완전히 동일한 문구, 혹은 동의어 수준의 표현(예: "의미" vs "뜻")은 작성하지 않습니다.
6. 단어 뜻이 불명할 경우 문맥 기반으로 가장 비슷한 사전적 의미의 "한국어 뜻"을 제공합니다.
7. 결과는 반드시 다음 JSON 형식으로만 출력합니다:

{{
  "videoId": "{video_id}",
  "result": {{
    "단어1": {{
      "품사": "n",
      "뜻": ["뜻1", "뜻2"]
    }},
    "단어2": {{
      "품사": "v",
      "뜻": ["뜻1"]
    }},
    "단어3": {{
      "품사": "adj",
      "뜻": ["뜻1", "뜻2"]
    }}
  }}
}}

중요:
- 단어의 뜻에 "..." 및 "중국어", "한자"의 사용을 금지합니다.
- 단어는 반드시 소문자로 정규화해서 사용하세요.
- **같은 의미가 반복되거나 동일 의미를 표현하는 문장을 두 번 작성하지 마세요.**
- JSON 외의 텍스트는 절대 포함하지 마세요.
- JSON 형식이 유효하지 않으면 파싱이 실패하므로, 반드시 유효한 JSON만 출력하세요.
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
2. **두 단어 이상으로 이루어진 표현**만 숙어로 인정합니다. 단일 단어(예: "revolutionizing")나 단순 명사/동사는 절대로 포함하지 마세요.
3. 숙어는 문맥상 특별한 의미 또는 관용적 의미가 드러나는 표현만 선택합니다. 단순히 빈출하는 일반 조합(예: "new technology")은 제외합니다.
4. 각 숙어에 대한 뜻은 문맥상 자연스러운 "한국어"로 제공합니다.
5. 결과는 반드시 다음 JSON 형식으로 반환해야 합니다:

{{
  "videoId": "{video_id}",
  "result": {{
    "숙어1": "뜻1",
    "숙어2": "뜻2",
    "숙어3": "뜻3"
  }}
}}

중요:
- 일반적인 단어 조합은 제외하고, 의미가 특별한 숙어만 추출하세요.
- **단일 단어이거나 공백이 없는 표현은 무조건 제외**하고, 최소 두 개 이상의 토큰을 가진 표현만 작성하세요.
- 숙어의 뜻에 "..." 및 "중국어", "한자"의 사용을 금지합니다.
- JSON 외의 텍스트는 절대 포함하지 마세요.
- JSON 형식이 유효하지 않으면 파싱이 실패하므로, 반드시 유효한 JSON만 출력하세요.
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
1. 각 단어에 대해 영어 동의어(synonym)를 "최대 2개까지" 제공합니다.
    - 동의어는 반드시 영어 단어로 제공해야 합니다.
    - 한글 뜻이 아닌 영어 단어를 제공하세요.
2. 각 단어에 대해 원본 텍스트에서 사용된 의미를 고려한 원본과는 다른 새로운 영어 예문을 "반드시 1개" 제공합니다.
    - 예문은 반드시 영어로 작성해야 합니다.
    - 한글이 아닌 영어 문장으로 작성하세요.
3. 결과는 반드시 다음 JSON 형식으로 반환해야 합니다:

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
- JSON 외의 텍스트는 절대 포함하지 마세요.
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
1. 각 숙어에 대해 원본 텍스트에서 사용된 의미를 고려한 원본과는 다른 새로운 영어 예문을 "반드시 1개" 제공합니다.
    - 예문은 반드시 영어로 작성해야 합니다.
    - 한글이 아닌 영어 문장으로 작성하세요.
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
- JSON 외의 텍스트는 절대 포함하지 마세요.
- JSON 형식이 유효하지 않으면 파싱이 실패하므로, 반드시 유효한 JSON만 출력하세요.
"""

