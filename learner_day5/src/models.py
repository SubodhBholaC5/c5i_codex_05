from dataclasses import dataclass, field

@dataclass(frozen=True)
class DraftRequest:
    case_id: str
    customer_message: str
    order_id: str | None = None
    locale: str = "en"
    conversation_id: str | None = None

@dataclass
class DraftResponse:
    case_id: str
    draft: str
    evidence: list[dict[str, str | bool | None]] = field(default_factory=list)
    needs_human_review: bool = False
    review_reasons: list[str] = field(default_factory=list)
    usage: dict[str, int | float] = field(default_factory=dict)
    request_id: str = ""

class ContractError(ValueError):
    pass
