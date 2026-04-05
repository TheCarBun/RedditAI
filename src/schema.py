from pydantic import BaseModel, Field
from typing import Literal, List, Optional


class OutputSchema(BaseModel):

    """
    A structured representation of analytical insights extracted from a Reddit post and its comments.
    """

    short_summary: str = Field(
        ...,
        description=(
            "A concise summary (1-2 minute read) capturing the essence of the discussion — "
            "the main ideas, tone, and overall topic."
        )
    )

    detailed_viewpoint_summary: str = Field(
        ...,
        description=(
            "An extended summary (under 10 minutes read) that explores different perspectives, "
            "arguments, and sides of the debate present in the comments."
        )
    )

    sentiment_analysis: Literal["positive", "negative", "neutral"] = Field(
        ...,
        description=(
            "Overall sentiment of the comment section — classified as positive, negative, or neutral "
            "based on general tone and language."
        )
    )

    emotion_detection: List[
        Literal[
            "joy", "sadness", "anger", "fear", "disgust",
            "surprise", "trust", "anticipation", "neutral"
        ]
    ] = Field(
        ...,
        description=(
            "List of dominant emotions detected in the comments. "
            "Multiple emotions can coexist if the discussion shows mixed tones."
        )
    )

    toxicity_detection: Optional[float] = Field(
        None,
        ge=0.0, le=1.0,
        description=(
            "A normalized toxicity score between 0 and 1, where 0 means non-toxic "
            "and 1 means highly toxic. Can be based on toxicity classifiers."
        )
    )

    ai_take: str = Field(
        ...,
        description=(
            "A short reflective paragraph from an AI perspective — summarizing or "
            "commenting on the overall discussion, its implications, or social tone."
        )
    )
