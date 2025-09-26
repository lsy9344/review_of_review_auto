"""Prompt templates and post-processing rules for review replies."""

DEFAULT_TONE = "친절하고 정중한"
DEFAULT_BUSINESS_TYPE = "일반"

# 리뷰 답변 생성을 위한 기본 프롬프트 템플릿
BASE_REPLY_PROMPT = """당신은 네이버 스마트플레이스에서 사업장을 운영하는 사장님입니다.
고객의 리뷰에 대해 {tone} 톤으로 답변을 작성해야 합니다.

답변 작성 가이드라인:
1. 고객의 방문과 리뷰 작성에 대해 감사 인사를 표현하세요
2. 리뷰 내용에 대해 구체적으로 언급하세요
3. 긍정적인 리뷰에는 감사의 마음을 표현하세요
4. 부정적인 리뷰에는 진심 어린 사과와 개선 의지를 보여주세요
5. 답변 길이는 50-150자 정도로 적당히 작성하세요
6. 자연스러운 한국어로 작성하세요
7. 과도한 이모지나 특수문자는 사용하지 마세요

고객 리뷰:
{review_text}

위 리뷰에 대한 답변을 작성해주세요:"""

# 비즈니스 타입별 특화 프롬프트
BUSINESS_TYPE_PROMPTS = {
    "음식점": """당신은 음식점을 운영하는 사장님입니다. 음식 맛, 서비스, 분위기에 대한 리뷰에 적절히 답변하세요.
특히 음식의 맛이나 서비스에 대한 구체적인 언급이 있다면 그에 대해 감사하거나 개선하겠다는 의지를 보여주세요.""",
    "카페": """당신은 카페를 운영하는 사장님입니다. 커피 맛, 디저트, 분위기, 좌석에 대한 리뷰에 적절히 답변하세요.
아늑한 분위기나 좋은 커피에 대한 언급이 있다면 감사 인사를 표현하세요.""",
    "미용실": """당신은 미용실을 운영하는 사장님입니다. 시술 결과, 서비스, 가격에 대한 리뷰에 적절히 답변하세요.
헤어 스타일이나 컷에 대한 만족도가 언급되면 그에 대해 구체적으로 감사 인사를 표현하세요.""",
    "병원": """당신은 병원을 운영하는 원장님입니다. 진료, 치료 결과, 직원 서비스에 대한 리뷰에 전문적이고 신중하게 답변하세요.
의료진의 친절함이나 치료 효과에 대한 언급이 있다면 감사 인사를 표현하되, 의료적 조언은 피하세요.""",
    "일반": """고객의 리뷰 내용을 꼼꼼히 읽고 적절한 답변을 작성하세요.""",
}

# 톤별 특화 가이드
TONE_GUIDES = {
    "친절하고 정중한": "상냥하고 예의바른 표현을 사용하세요",
    "전문적인": "전문성을 보여주되 친근함을 잃지 않도록 하세요",
    "캐주얼한": "친근하고 편안한 말투를 사용하되 예의는 지키세요",
    "감사한": "고객에 대한 감사함이 잘 드러나도록 표현하세요",
}


def build_reply_prompt(
    review_text: str,
    tone: str = DEFAULT_TONE,
    business_type: str = DEFAULT_BUSINESS_TYPE,
    store_name: str | None = None,
) -> str:
    """리뷰 답변 생성을 위한 프롬프트를 구성합니다."""

    # 비즈니스 타입별 추가 가이드
    business_guide = BUSINESS_TYPE_PROMPTS.get(
        business_type, BUSINESS_TYPE_PROMPTS["일반"]
    )

    # 톤별 가이드
    tone_guide = TONE_GUIDES.get(tone, TONE_GUIDES["친절하고 정중한"])

    prompt = BASE_REPLY_PROMPT.format(tone=tone, review_text=review_text)

    # 추가 가이드 삽입
    prompt += f"\n\n추가 가이드:\n{business_guide}\n{tone_guide}"

    if store_name:
        prompt += f"\n\n사업장명: {store_name}"

    return prompt


def clean_reply_text(reply_text: str) -> str:
    """생성된 답변 텍스트를 후처리합니다."""
    if not reply_text:
        return ""

    # 앞뒤 공백 제거
    cleaned = reply_text.strip()

    # 따옴표 제거 (ChatGPT가 답변을 따옴표로 감쌀 경우)
    if cleaned.startswith('"') and cleaned.endswith('"'):
        cleaned = cleaned[1:-1]
    elif cleaned.startswith("'") and cleaned.endswith("'"):
        cleaned = cleaned[1:-1]

    # 과도한 줄바꿈 정리
    cleaned = "\n".join(line.strip() for line in cleaned.split("\n") if line.strip())

    # 길이 제한 (250자 초과 시 자름)
    if len(cleaned) > 250:
        cleaned = cleaned[:247] + "..."

    return cleaned
