"""
프롬프트 A/B 테스트용 프롬프트 함수들

이 파일은 practice/phase4/prompt_ab_test.py에서 추출한 프롬프트 함수들을 포함합니다.
"""
from typing import Dict, Any

def get_word_extraction_prompt_v1(chunk_text: str, video_id: str) -> str:
    """버전 1: 출력 형식 앞에 배치, 강한 강조"""
    return f"""
결과는 반드시 다음 JSON 형식으로만 출력합니다:

{{
  "videoId": "{video_id}",
  "result": {{
    "단어1": {{"품사": "n", "뜻": ["뜻1", "뜻2"]}},
    "단어2": {{"품사": "v", "뜻": ["뜻1"]}}
  }}
}}

⚠️ 중요: 마크다운 코드 블록(```json 또는 ```)을 절대 사용하지 마세요. 순수 JSON만 출력하세요.
⚠️ 중요: JSON 외의 텍스트는 절대 포함하지 마세요.

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

⚠️ 중요: 단어의 뜻에 "..." 및 "중국어", "한자"의 사용을 금지합니다.
⚠️ 중요: 단어의 뜻에 "masc.:", "female:", "남성:", "여성:" 등 성별 구분 표기를 절대 사용하지 마세요.
⚠️ 중요: 단어는 반드시 소문자로 정규화해서 사용하세요.
⚠️ 중요: 같은 의미가 반복되거나 동일 의미를 표현하는 문장을 두 번 작성하지 마세요.
"""


def get_word_extraction_prompt_v2(chunk_text: str, video_id: str) -> str:
    """버전 2: 출력 형식 앞에 배치, 예시 포함"""
    return f"""
결과는 반드시 다음 JSON 형식으로만 출력합니다:

{{
  "videoId": "{video_id}",
  "result": {{
    "artificial": {{"품사": "adj", "뜻": ["인공의", "가짜의"]}},
    "intelligence": {{"품사": "n", "뜻": ["지능", "지성"]}},
    "revolutionize": {{"품사": "v", "뜻": ["혁신하다"]}}
  }}
}}

⚠️ 중요: 마크다운 코드 블록(```json 또는 ```)을 절대 사용하지 마세요. 순수 JSON만 출력하세요.
⚠️ 중요: JSON 외의 텍스트는 절대 포함하지 마세요.

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

⚠️ 중요: 단어의 뜻에 "..." 및 "중국어", "한자"의 사용을 금지합니다.
⚠️ 중요: 단어의 뜻에 "masc.:", "female:", "남성:", "여성:" 등 성별 구분 표기를 절대 사용하지 마세요.
⚠️ 중요: 단어는 반드시 소문자로 정규화해서 사용하세요.
⚠️ 중요: 같은 의미가 반복되거나 동일 의미를 표현하는 문장을 두 번 작성하지 마세요.
"""


def get_word_extraction_prompt_v3(chunk_text: str, video_id: str) -> str:
    """버전 3: 출력 형식 앞에 배치, 실패 예시 포함"""
    return f"""
결과는 반드시 다음 JSON 형식으로만 출력합니다:

{{
  "videoId": "{video_id}",
  "result": {{
    "단어1": {{"품사": "n", "뜻": ["뜻1", "뜻2"]}},
    "단어2": {{"품사": "v", "뜻": ["뜻1"]}}
  }}
}}

❌ 잘못된 출력 예시:
```json
{{"videoId": "...", "result": {{...}}}}
```
위의 JSON은 올바르게 생성되었으나... (추가 설명)

✅ 올바른 출력: 위 JSON 형식 그대로, 추가 설명 없이 순수 JSON만 출력하세요.

⚠️ 중요: 마크다운 코드 블록(```json 또는 ```)을 절대 사용하지 마세요. 순수 JSON만 출력하세요.
⚠️ 중요: JSON 외의 텍스트는 절대 포함하지 마세요.

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

⚠️ 중요: 단어의 뜻에 "..." 및 "중국어", "한자"의 사용을 금지합니다.
⚠️ 중요: 단어의 뜻에 "masc.:", "female:", "남성:", "여성:" 등 성별 구분 표기를 절대 사용하지 마세요.
⚠️ 중요: 단어는 반드시 소문자로 정규화해서 사용하세요.
⚠️ 중요: 같은 의미가 반복되거나 동일 의미를 표현하는 문장을 두 번 작성하지 마세요.
"""


def get_word_extraction_prompt_v4(chunk_text: str, video_id: str) -> str:
    """버전 4: 출력 형식 중간에 배치, 강한 강조"""
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

⚠️ 중요: 단어의 뜻에 "..." 및 "중국어", "한자"의 사용을 금지합니다.
⚠️ 중요: 단어의 뜻에 "masc.:", "female:", "남성:", "여성:" 등 성별 구분 표기를 절대 사용하지 마세요.
⚠️ 중요: 단어는 반드시 소문자로 정규화해서 사용하세요.
⚠️ 중요: 같은 의미가 반복되거나 동일 의미를 표현하는 문장을 두 번 작성하지 마세요.

결과는 반드시 다음 JSON 형식으로만 출력합니다:

{{
  "videoId": "{video_id}",
  "result": {{
    "단어1": {{"품사": "n", "뜻": ["뜻1", "뜻2"]}},
    "단어2": {{"품사": "v", "뜻": ["뜻1"]}}
  }}
}}

⚠️ 중요: 마크다운 코드 블록(```json 또는 ```)을 절대 사용하지 마세요. 순수 JSON만 출력하세요.
⚠️ 중요: JSON 외의 텍스트는 절대 포함하지 마세요.
⚠️ 중요: JSON 형식이 유효하지 않으면 파싱이 실패하므로, 반드시 유효한 JSON만 출력하세요.
"""


def get_word_extraction_prompt_v5(chunk_text: str, video_id: str) -> str:
    """버전 5: 출력 형식 중간에 배치, 예시 포함"""
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

⚠️ 중요: 단어의 뜻에 "..." 및 "중국어", "한자"의 사용을 금지합니다.
⚠️ 중요: 단어의 뜻에 "masc.:", "female:", "남성:", "여성:" 등 성별 구분 표기를 절대 사용하지 마세요.
⚠️ 중요: 단어는 반드시 소문자로 정규화해서 사용하세요.
⚠️ 중요: 같은 의미가 반복되거나 동일 의미를 표현하는 문장을 두 번 작성하지 마세요.

결과는 반드시 다음 JSON 형식으로만 출력합니다 (예시):

{{
  "videoId": "{video_id}",
  "result": {{
    "artificial": {{"품사": "adj", "뜻": ["인공의", "가짜의"]}},
    "intelligence": {{"품사": "n", "뜻": ["지능", "지성"]}},
    "revolutionize": {{"품사": "v", "뜻": ["혁신하다"]}}
  }}
}}

⚠️ 중요: 마크다운 코드 블록(```json 또는 ```)을 절대 사용하지 마세요. 순수 JSON만 출력하세요.
⚠️ 중요: JSON 외의 텍스트는 절대 포함하지 마세요.
⚠️ 중요: JSON 형식이 유효하지 않으면 파싱이 실패하므로, 반드시 유효한 JSON만 출력하세요.
"""


def get_word_extraction_prompt_v6(chunk_text: str, video_id: str) -> str:
    """버전 6: 출력 형식 중간에 배치, 실패 예시 포함"""
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

⚠️ 중요: 단어의 뜻에 "..." 및 "중국어", "한자"의 사용을 금지합니다.
⚠️ 중요: 단어의 뜻에 "masc.:", "female:", "남성:", "여성:" 등 성별 구분 표기를 절대 사용하지 마세요.
⚠️ 중요: 단어는 반드시 소문자로 정규화해서 사용하세요.
⚠️ 중요: 같은 의미가 반복되거나 동일 의미를 표현하는 문장을 두 번 작성하지 마세요.

결과는 반드시 다음 JSON 형식으로만 출력합니다:

{{
  "videoId": "{video_id}",
  "result": {{
    "단어1": {{"품사": "n", "뜻": ["뜻1", "뜻2"]}},
    "단어2": {{"품사": "v", "뜻": ["뜻1"]}}
  }}
}}

❌ 잘못된 출력 예시:
```json
{{"videoId": "...", "result": {{...}}}}
```
위의 JSON은 올바르게 생성되었으나... (추가 설명)

✅ 올바른 출력: 위 JSON 형식 그대로, 추가 설명 없이 순수 JSON만 출력하세요.

⚠️ 중요: 마크다운 코드 블록(```json 또는 ```)을 절대 사용하지 마세요. 순수 JSON만 출력하세요.
⚠️ 중요: JSON 외의 텍스트는 절대 포함하지 마세요.
"""


def get_word_extraction_prompt_v7(chunk_text: str, video_id: str) -> str:
    """버전 7: 출력 형식 뒤에 배치, 강한 강조"""
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

⚠️ 중요: 단어의 뜻에 "..." 및 "중국어", "한자"의 사용을 금지합니다.
⚠️ 중요: 단어의 뜻에 "masc.:", "female:", "남성:", "여성:" 등 성별 구분 표기를 절대 사용하지 마세요.
⚠️ 중요: 단어는 반드시 소문자로 정규화해서 사용하세요.
⚠️ 중요: 같은 의미가 반복되거나 동일 의미를 표현하는 문장을 두 번 작성하지 마세요.

결과는 반드시 다음 JSON 형식으로만 출력합니다:

{{
  "videoId": "{video_id}",
  "result": {{
    "단어1": {{"품사": "n", "뜻": ["뜻1", "뜻2"]}},
    "단어2": {{"품사": "v", "뜻": ["뜻1"]}}
  }}
}}

⚠️⚠️⚠️ 최종 확인 사항 ⚠️⚠️⚠️
1. 마크다운 코드 블록(```json 또는 ```)을 절대 사용하지 마세요. 순수 JSON만 출력하세요.
2. JSON 외의 텍스트는 절대 포함하지 마세요.
3. JSON 형식이 유효하지 않으면 파싱이 실패하므로, 반드시 유효한 JSON만 출력하세요.
4. 출력은 JSON만 있어야 하며, 그 앞이나 뒤에 설명이나 주석을 추가하지 마세요.
"""


def get_word_extraction_prompt_v8(chunk_text: str, video_id: str) -> str:
    """버전 8: 출력 형식 뒤에 배치, 예시 포함"""
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

⚠️ 중요: 단어의 뜻에 "..." 및 "중국어", "한자"의 사용을 금지합니다.
⚠️ 중요: 단어의 뜻에 "masc.:", "female:", "남성:", "여성:" 등 성별 구분 표기를 절대 사용하지 마세요.
⚠️ 중요: 단어는 반드시 소문자로 정규화해서 사용하세요.
⚠️ 중요: 같은 의미가 반복되거나 동일 의미를 표현하는 문장을 두 번 작성하지 마세요.

결과는 반드시 다음 JSON 형식으로만 출력합니다 (예시):

{{
  "videoId": "{video_id}",
  "result": {{
    "artificial": {{"품사": "adj", "뜻": ["인공의", "가짜의"]}},
    "intelligence": {{"품사": "n", "뜻": ["지능", "지성"]}},
    "revolutionize": {{"품사": "v", "뜻": ["혁신하다"]}}
  }}
}}

⚠️⚠️⚠️ 최종 확인 사항 ⚠️⚠️⚠️
1. 마크다운 코드 블록(```json 또는 ```)을 절대 사용하지 마세요. 순수 JSON만 출력하세요.
2. JSON 외의 텍스트는 절대 포함하지 마세요.
3. JSON 형식이 유효하지 않으면 파싱이 실패하므로, 반드시 유효한 JSON만 출력하세요.
4. 출력은 JSON만 있어야 하며, 그 앞이나 뒤에 설명이나 주석을 추가하지 마세요.
"""


def get_word_extraction_prompt_v9(chunk_text: str, video_id: str) -> str:
    """버전 9: 출력 형식 뒤에 배치, 실패 예시 포함"""
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

⚠️ 중요: 단어의 뜻에 "..." 및 "중국어", "한자"의 사용을 금지합니다.
⚠️ 중요: 단어의 뜻에 "masc.:", "female:", "남성:", "여성:" 등 성별 구분 표기를 절대 사용하지 마세요.
⚠️ 중요: 단어는 반드시 소문자로 정규화해서 사용하세요.
⚠️ 중요: 같은 의미가 반복되거나 동일 의미를 표현하는 문장을 두 번 작성하지 마세요.

결과는 반드시 다음 JSON 형식으로만 출력합니다:

{{
  "videoId": "{video_id}",
  "result": {{
    "단어1": {{"품사": "n", "뜻": ["뜻1", "뜻2"]}},
    "단어2": {{"품사": "v", "뜻": ["뜻1"]}}
  }}
}}

❌ 잘못된 출력 예시:
```json
{{"videoId": "...", "result": {{...}}}}
```
위의 JSON은 올바르게 생성되었으나... (추가 설명)

✅ 올바른 출력: 위 JSON 형식 그대로, 추가 설명 없이 순수 JSON만 출력하세요.

⚠️⚠️⚠️ 최종 확인 사항 ⚠️⚠️⚠️
1. 마크다운 코드 블록(```json 또는 ```)을 절대 사용하지 마세요. 순수 JSON만 출력하세요.
2. JSON 외의 텍스트는 절대 포함하지 마세요.
3. JSON 형식이 유효하지 않으면 파싱이 실패하므로, 반드시 유효한 JSON만 출력하세요.
4. 출력은 JSON만 있어야 하며, 그 앞이나 뒤에 설명이나 주석을 추가하지 마세요.
"""


def get_word_extraction_prompt_v10(chunk_text: str, video_id: str) -> str:
    """버전 10: 출력 형식 뒤에 배치, 간결한 강조"""
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


def get_phrase_extraction_prompt_v1(chunk_text: str, video_id: str) -> str:
    """버전 1: 출력 형식 앞에 배치, 강한 강조"""
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


def get_phrase_extraction_prompt_v2(chunk_text: str, video_id: str) -> str:
    """버전 2: 출력 형식 앞에 배치, 예시 포함"""
    return f"""
결과는 반드시 다음 JSON 형식으로만 출력합니다:

{{
  "videoId": "{video_id}",
  "result": {{
    "think outside the box": "창의적으로 생각하다",
    "keep pace with": "따라잡다",
    "take stock of": "검토하다"
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


def get_phrase_extraction_prompt_v3(chunk_text: str, video_id: str) -> str:
    """버전 3: 출력 형식 앞에 배치, 실패 예시 포함"""
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

❌ 잘못된 출력 예시:
```json
{{"videoId": "...", "result": {{...}}}}
```
위의 JSON은 올바르게 생성되었으나... (추가 설명)

✅ 올바른 출력: 위 JSON 형식 그대로, 추가 설명 없이 순수 JSON만 출력하세요.

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


def get_phrase_extraction_prompt_v4(chunk_text: str, video_id: str) -> str:
    """버전 4: 출력 형식 중간에 배치, 강한 강조"""
    return f"""
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
⚠️ 중요: JSON 형식이 유효하지 않으면 파싱이 실패하므로, 반드시 유효한 JSON만 출력하세요.
"""


def get_phrase_extraction_prompt_v5(chunk_text: str, video_id: str) -> str:
    """버전 5: 출력 형식 중간에 배치, 예시 포함"""
    return f"""
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

결과는 반드시 다음 JSON 형식으로만 출력합니다 (예시):

{{
  "videoId": "{video_id}",
  "result": {{
    "think outside the box": "창의적으로 생각하다",
    "keep pace with": "따라잡다",
    "take stock of": "검토하다"
  }}
}}

⚠️ 중요: 마크다운 코드 블록(```json 또는 ```)을 절대 사용하지 마세요. 순수 JSON만 출력하세요.
⚠️ 중요: JSON 외의 텍스트는 절대 포함하지 마세요.
⚠️ 중요: JSON 형식이 유효하지 않으면 파싱이 실패하므로, 반드시 유효한 JSON만 출력하세요.
"""


def get_phrase_extraction_prompt_v6(chunk_text: str, video_id: str) -> str:
    """버전 6: 출력 형식 중간에 배치, 실패 예시 포함"""
    return f"""
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

결과는 반드시 다음 JSON 형식으로만 출력합니다:

{{
  "videoId": "{video_id}",
  "result": {{
    "숙어1": "뜻1",
    "숙어2": "뜻2",
    "숙어3": "뜻3"
  }}
}}

❌ 잘못된 출력 예시:
```json
{{"videoId": "...", "result": {{...}}}}
```
위의 JSON은 올바르게 생성되었으나... (추가 설명)

✅ 올바른 출력: 위 JSON 형식 그대로, 추가 설명 없이 순수 JSON만 출력하세요.

⚠️ 중요: 마크다운 코드 블록(```json 또는 ```)을 절대 사용하지 마세요. 순수 JSON만 출력하세요.
⚠️ 중요: JSON 외의 텍스트는 절대 포함하지 마세요.
"""


def get_phrase_extraction_prompt_v7(chunk_text: str, video_id: str) -> str:
    """버전 7: 출력 형식 뒤에 배치, 강한 강조"""
    return f"""
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

결과는 반드시 다음 JSON 형식으로만 출력합니다:

{{
  "videoId": "{video_id}",
  "result": {{
    "숙어1": "뜻1",
    "숙어2": "뜻2",
    "숙어3": "뜻3"
  }}
}}

⚠️⚠️⚠️ 최종 확인 사항 ⚠️⚠️⚠️
1. 마크다운 코드 블록(```json 또는 ```)을 절대 사용하지 마세요. 순수 JSON만 출력하세요.
2. JSON 외의 텍스트는 절대 포함하지 마세요.
3. JSON 형식이 유효하지 않으면 파싱이 실패하므로, 반드시 유효한 JSON만 출력하세요.
4. 출력은 JSON만 있어야 하며, 그 앞이나 뒤에 설명이나 주석을 추가하지 마세요.
"""


def get_phrase_extraction_prompt_v8(chunk_text: str, video_id: str) -> str:
    """버전 8: 출력 형식 뒤에 배치, 예시 포함"""
    return f"""
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

결과는 반드시 다음 JSON 형식으로만 출력합니다 (예시):

{{
  "videoId": "{video_id}",
  "result": {{
    "think outside the box": "창의적으로 생각하다",
    "keep pace with": "따라잡다",
    "take stock of": "검토하다"
  }}
}}

⚠️⚠️⚠️ 최종 확인 사항 ⚠️⚠️⚠️
1. 마크다운 코드 블록(```json 또는 ```)을 절대 사용하지 마세요. 순수 JSON만 출력하세요.
2. JSON 외의 텍스트는 절대 포함하지 마세요.
3. JSON 형식이 유효하지 않으면 파싱이 실패하므로, 반드시 유효한 JSON만 출력하세요.
4. 출력은 JSON만 있어야 하며, 그 앞이나 뒤에 설명이나 주석을 추가하지 마세요.
"""


def get_phrase_extraction_prompt_v9(chunk_text: str, video_id: str) -> str:
    """버전 9: 출력 형식 뒤에 배치, 실패 예시 포함"""
    return f"""
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

결과는 반드시 다음 JSON 형식으로만 출력합니다:

{{
  "videoId": "{video_id}",
  "result": {{
    "숙어1": "뜻1",
    "숙어2": "뜻2",
    "숙어3": "뜻3"
  }}
}}

❌ 잘못된 출력 예시:
```json
{{"videoId": "...", "result": {{...}}}}
```
위의 JSON은 올바르게 생성되었으나... (추가 설명)

✅ 올바른 출력: 위 JSON 형식 그대로, 추가 설명 없이 순수 JSON만 출력하세요.

⚠️⚠️⚠️ 최종 확인 사항 ⚠️⚠️⚠️
1. 마크다운 코드 블록(```json 또는 ```)을 절대 사용하지 마세요. 순수 JSON만 출력하세요.
2. JSON 외의 텍스트는 절대 포함하지 마세요.
3. JSON 형식이 유효하지 않으면 파싱이 실패하므로, 반드시 유효한 JSON만 출력하세요.
4. 출력은 JSON만 있어야 하며, 그 앞이나 뒤에 설명이나 주석을 추가하지 마세요.
"""


def get_phrase_extraction_prompt_v10(chunk_text: str, video_id: str) -> str:
    """버전 10: 출력 형식 뒤에 배치, 간결한 강조"""
    return f"""
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

중요:
- 일반적인 단어 조합은 제외하고, 의미가 특별한 숙어만 추출하세요.
- 단일 단어이거나 공백이 없는 표현은 무조건 제외하고, 최소 두 개 이상의 토큰을 가진 표현만 작성하세요.
- 숙어의 뜻에 "..." 및 "중국어", "한자"의 사용을 금지합니다.

결과는 반드시 다음 JSON 형식으로만 출력합니다:

{{
  "videoId": "{video_id}",
  "result": {{
    "숙어1": "뜻1",
    "숙어2": "뜻2",
    "숙어3": "뜻3"
  }}
}}

중요:
- 마크다운 코드 블록(```json 또는 ```)을 절대 사용하지 마세요. 순수 JSON만 출력하세요.
- JSON 외의 텍스트는 절대 포함하지 마세요.
- JSON 형식이 유효하지 않으면 파싱이 실패하므로, 반드시 유효한 JSON만 출력하세요.
"""


def get_word_enrichment_prompt_v1(words: Dict[str, Dict[str, Any]], video_id: str) -> str:
    """버전 1: 출력 형식 앞에 배치, 강한 강조"""
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


def get_word_enrichment_prompt_v2(words: Dict[str, Dict[str, Any]], video_id: str) -> str:
    """버전 2: 출력 형식 앞에 배치, 예시 포함"""
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
    "innovation": {{
      "동의어": ["creativity", "invention"],
      "예문": "The company's innovation led to breakthrough products."
    }},
    "strive": {{
      "동의어": ["endeavor", "attempt"],
      "예문": "We must strive to achieve our goals."
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


def get_word_enrichment_prompt_v3(words: Dict[str, Dict[str, Any]], video_id: str) -> str:
    """버전 3: 출력 형식 중간에 배치, 강한 강조"""
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

⚠️ 중요: 동의어와 예문은 반드시 영어로 작성해야 합니다. 한글을 사용하지 마세요.

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
"""


def get_word_enrichment_prompt_v4(words: Dict[str, Dict[str, Any]], video_id: str) -> str:
    """버전 4: 출력 형식 중간에 배치, 예시 포함"""
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

결과는 반드시 다음 JSON 형식으로만 출력합니다 (예시):

{{
  "videoId": "{video_id}",
  "result": {{
    "innovation": {{
      "동의어": ["creativity", "invention"],
      "예문": "The company's innovation led to breakthrough products."
    }},
    "strive": {{
      "동의어": ["endeavor", "attempt"],
      "예문": "We must strive to achieve our goals."
    }}
  }}
}}

⚠️ 중요: 마크다운 코드 블록(```json 또는 ```)을 절대 사용하지 마세요. 순수 JSON만 출력하세요.
⚠️ 중요: JSON 외의 텍스트는 절대 포함하지 마세요.
"""


def get_word_enrichment_prompt_v5(words: Dict[str, Dict[str, Any]], video_id: str) -> str:
    """버전 5: 출력 형식 뒤에 배치, 강한 강조"""
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

⚠️⚠️⚠️ 최종 확인 사항 ⚠️⚠️⚠️
1. 마크다운 코드 블록(```json 또는 ```)을 절대 사용하지 마세요. 순수 JSON만 출력하세요.
2. JSON 외의 텍스트는 절대 포함하지 마세요.
3. 동의어와 예문은 반드시 영어로 작성해야 합니다.
4. 출력은 JSON만 있어야 하며, 그 앞이나 뒤에 설명이나 주석을 추가하지 마세요.
"""


def get_word_enrichment_prompt_v6(words: Dict[str, Dict[str, Any]], video_id: str) -> str:
    """버전 6: 출력 형식 뒤에 배치, 예시 포함"""
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

결과는 반드시 다음 JSON 형식으로만 출력합니다 (예시):

{{
  "videoId": "{video_id}",
  "result": {{
    "innovation": {{
      "동의어": ["creativity", "invention"],
      "예문": "The company's innovation led to breakthrough products."
    }},
    "strive": {{
      "동의어": ["endeavor", "attempt"],
      "예문": "We must strive to achieve our goals."
    }}
  }}
}}

⚠️⚠️⚠️ 최종 확인 사항 ⚠️⚠️⚠️
1. 마크다운 코드 블록(```json 또는 ```)을 절대 사용하지 마세요. 순수 JSON만 출력하세요.
2. JSON 외의 텍스트는 절대 포함하지 마세요.
3. 동의어와 예문은 반드시 영어로 작성해야 합니다.
4. 출력은 JSON만 있어야 하며, 그 앞이나 뒤에 설명이나 주석을 추가하지 마세요.
"""


def get_word_enrichment_prompt_v7(words: Dict[str, Dict[str, Any]], video_id: str) -> str:
    """버전 7: 출력 형식 뒤에 배치, 간결한 강조"""
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


def get_word_enrichment_prompt_v8(words: Dict[str, Dict[str, Any]], video_id: str) -> str:
    """버전 8: 출력 형식 앞에 배치, 실패 예시 포함"""
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

❌ 잘못된 출력 예시:
```json
{{"videoId": "...", "result": {{...}}}}
```
위의 JSON은 올바르게 생성되었으나... (추가 설명)

✅ 올바른 출력: 위 JSON 형식 그대로, 추가 설명 없이 순수 JSON만 출력하세요.

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


def get_word_enrichment_prompt_v9(words: Dict[str, Dict[str, Any]], video_id: str) -> str:
    """버전 9: 출력 형식 중간에 배치, 실패 예시 포함"""
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

❌ 잘못된 출력 예시:
```json
{{"videoId": "...", "result": {{...}}}}
```
위의 JSON은 올바르게 생성되었으나... (추가 설명)

✅ 올바른 출력: 위 JSON 형식 그대로, 추가 설명 없이 순수 JSON만 출력하세요.

⚠️ 중요: 마크다운 코드 블록(```json 또는 ```)을 절대 사용하지 마세요. 순수 JSON만 출력하세요.
⚠️ 중요: JSON 외의 텍스트는 절대 포함하지 마세요.
"""


def get_word_enrichment_prompt_v10(words: Dict[str, Dict[str, Any]], video_id: str) -> str:
    """버전 10: 출력 형식 뒤에 배치, 간결한 강조 (v10 스타일)"""
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

중요:
- 동의어와 예문은 반드시 영어로 작성해야 합니다. 한글을 사용하지 마세요.
- 단어의 품사와 뜻을 고려하여 적절한 동의어를 선택하세요.

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
- JSON 형식이 유효하지 않으면 파싱이 실패하므로, 반드시 유효한 JSON만 출력하세요.
"""


def get_phrase_enrichment_prompt_v1(phrases: Dict[str, str], video_id: str) -> str:
    """버전 1: 출력 형식 앞에 배치, 강한 강조"""
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


def get_phrase_enrichment_prompt_v2(phrases: Dict[str, str], video_id: str) -> str:
    """버전 2: 출력 형식 앞에 배치, 예시 포함"""
    phrases_str = "\n".join([f"- {phrase}: {meaning}" for phrase, meaning in phrases.items()])
    
    return f"""
결과는 반드시 다음 JSON 형식으로만 출력합니다:

{{
  "videoId": "{video_id}",
  "result": {{
    "think outside the box": {{
      "예문": "We need to think outside the box to solve this problem."
    }},
    "keep pace with": {{
      "예문": "Companies must keep pace with technological changes."
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


def get_phrase_enrichment_prompt_v3(phrases: Dict[str, str], video_id: str) -> str:
    """버전 3: 출력 형식 중간에 배치, 강한 강조"""
    phrases_str = "\n".join([f"- {phrase}: {meaning}" for phrase, meaning in phrases.items()])
    
    return f"""
다음 숙어들에 대해 해당 숙어를 사용한 간단한 영어 예문을 생성해주세요.

숙어 목록:
{phrases_str}

요구사항:
1. 각 숙어에 대해 해당 숙어를 사용한 간단한 영어 예문을 "반드시 1개" 제공합니다.
2. 예문은 반드시 영어로 작성해야 합니다.

⚠️ 중요: 예문은 반드시 영어로 작성해야 합니다. 한글을 사용하지 마세요.

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
"""


def get_phrase_enrichment_prompt_v4(phrases: Dict[str, str], video_id: str) -> str:
    """버전 4: 출력 형식 중간에 배치, 예시 포함"""
    phrases_str = "\n".join([f"- {phrase}: {meaning}" for phrase, meaning in phrases.items()])
    
    return f"""
다음 숙어들에 대해 해당 숙어를 사용한 간단한 영어 예문을 생성해주세요.

숙어 목록:
{phrases_str}

요구사항:
1. 각 숙어에 대해 해당 숙어를 사용한 간단한 영어 예문을 "반드시 1개" 제공합니다.
2. 예문은 반드시 영어로 작성해야 합니다.

결과는 반드시 다음 JSON 형식으로만 출력합니다 (예시):

{{
  "videoId": "{video_id}",
  "result": {{
    "think outside the box": {{
      "예문": "We need to think outside the box to solve this problem."
    }},
    "keep pace with": {{
      "예문": "Companies must keep pace with technological changes."
    }}
  }}
}}

⚠️ 중요: 마크다운 코드 블록(```json 또는 ```)을 절대 사용하지 마세요. 순수 JSON만 출력하세요.
⚠️ 중요: JSON 외의 텍스트는 절대 포함하지 마세요.
"""


def get_phrase_enrichment_prompt_v5(phrases: Dict[str, str], video_id: str) -> str:
    """버전 5: 출력 형식 뒤에 배치, 강한 강조"""
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

⚠️⚠️⚠️ 최종 확인 사항 ⚠️⚠️⚠️
1. 마크다운 코드 블록(```json 또는 ```)을 절대 사용하지 마세요. 순수 JSON만 출력하세요.
2. JSON 외의 텍스트는 절대 포함하지 마세요.
3. 예문은 반드시 영어로 작성해야 합니다.
4. 출력은 JSON만 있어야 하며, 그 앞이나 뒤에 설명이나 주석을 추가하지 마세요.
"""


def get_phrase_enrichment_prompt_v6(phrases: Dict[str, str], video_id: str) -> str:
    """버전 6: 출력 형식 뒤에 배치, 예시 포함"""
    phrases_str = "\n".join([f"- {phrase}: {meaning}" for phrase, meaning in phrases.items()])
    
    return f"""
다음 숙어들에 대해 해당 숙어를 사용한 간단한 영어 예문을 생성해주세요.

숙어 목록:
{phrases_str}

요구사항:
1. 각 숙어에 대해 해당 숙어를 사용한 간단한 영어 예문을 "반드시 1개" 제공합니다.
2. 예문은 반드시 영어로 작성해야 합니다.

결과는 반드시 다음 JSON 형식으로만 출력합니다 (예시):

{{
  "videoId": "{video_id}",
  "result": {{
    "think outside the box": {{
      "예문": "We need to think outside the box to solve this problem."
    }},
    "keep pace with": {{
      "예문": "Companies must keep pace with technological changes."
    }}
  }}
}}

⚠️⚠️⚠️ 최종 확인 사항 ⚠️⚠️⚠️
1. 마크다운 코드 블록(```json 또는 ```)을 절대 사용하지 마세요. 순수 JSON만 출력하세요.
2. JSON 외의 텍스트는 절대 포함하지 마세요.
3. 예문은 반드시 영어로 작성해야 합니다.
4. 출력은 JSON만 있어야 하며, 그 앞이나 뒤에 설명이나 주석을 추가하지 마세요.
"""


def get_phrase_enrichment_prompt_v7(phrases: Dict[str, str], video_id: str) -> str:
    """버전 7: 출력 형식 뒤에 배치, 간결한 강조"""
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


def get_phrase_enrichment_prompt_v8(phrases: Dict[str, str], video_id: str) -> str:
    """버전 8: 출력 형식 앞에 배치, 실패 예시 포함"""
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

❌ 잘못된 출력 예시:
```json
{{"videoId": "...", "result": {{...}}}}
```
위의 JSON은 올바르게 생성되었으나... (추가 설명)

✅ 올바른 출력: 위 JSON 형식 그대로, 추가 설명 없이 순수 JSON만 출력하세요.

⚠️ 중요: 마크다운 코드 블록(```json 또는 ```)을 절대 사용하지 마세요. 순수 JSON만 출력하세요.
⚠️ 중요: JSON 외의 텍스트는 절대 포함하지 마세요.

다음 숙어들에 대해 해당 숙어를 사용한 간단한 영어 예문을 생성해주세요.

숙어 목록:
{phrases_str}

요구사항:
1. 각 숙어에 대해 해당 숙어를 사용한 간단한 영어 예문을 "반드시 1개" 제공합니다.
2. 예문은 반드시 영어로 작성해야 합니다.
"""


def get_phrase_enrichment_prompt_v9(phrases: Dict[str, str], video_id: str) -> str:
    """버전 9: 출력 형식 중간에 배치, 실패 예시 포함"""
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

❌ 잘못된 출력 예시:
```json
{{"videoId": "...", "result": {{...}}}}
```
위의 JSON은 올바르게 생성되었으나... (추가 설명)

✅ 올바른 출력: 위 JSON 형식 그대로, 추가 설명 없이 순수 JSON만 출력하세요.

⚠️ 중요: 마크다운 코드 블록(```json 또는 ```)을 절대 사용하지 마세요. 순수 JSON만 출력하세요.
⚠️ 중요: JSON 외의 텍스트는 절대 포함하지 마세요.
"""


def get_phrase_enrichment_prompt_v10(phrases: Dict[str, str], video_id: str) -> str:
    """버전 10: 출력 형식 뒤에 배치, 간결한 강조 (v10 스타일)"""
    phrases_str = "\n".join([f"- {phrase}: {meaning}" for phrase, meaning in phrases.items()])
    
    return f"""
다음 숙어들에 대해 해당 숙어를 사용한 간단한 영어 예문을 생성해주세요.

숙어 목록:
{phrases_str}

요구사항:
1. 각 숙어에 대해 해당 숙어를 사용한 간단한 영어 예문을 "반드시 1개" 제공합니다.
2. 예문은 반드시 영어로 작성해야 합니다.

중요:
- 예문은 반드시 영어로 작성해야 합니다. 한글을 사용하지 마세요.
- 숙어의 뜻에 맞는 자연스러운 예문을 작성하세요.

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
- JSON 형식이 유효하지 않으면 파싱이 실패하므로, 반드시 유효한 JSON만 출력하세요.
"""
