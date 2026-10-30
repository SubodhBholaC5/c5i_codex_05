from .models import DraftRequest, ContractError

def validate_request(payload: dict) -> DraftRequest:
    if not isinstance(payload, dict):
        raise ContractError("Request body must be a JSON object")
    allowed={"case_id","customer_message","order_id","locale","conversation_id"}
    unknown=set(payload)-allowed
    if unknown: raise ContractError(f"Unknown fields: {', '.join(sorted(unknown))}")
    case_id=payload.get("case_id"); message=payload.get("customer_message")
    if not isinstance(case_id,str) or not 1<=len(case_id)<=40: raise ContractError("case_id must be 1 to 40 characters")
    if not isinstance(message,str) or not message.strip() or len(message)>2000: raise ContractError("customer_message must be non-empty and at most 2000 characters")
    order_id=payload.get("order_id")
    if order_id is not None and (not isinstance(order_id,str) or len(order_id)>40): raise ContractError("order_id must be at most 40 characters")
    locale=payload.get("locale","en")
    if locale not in {"en","fr"}: raise ContractError("locale must be en or fr")
    conversation_id=payload.get("conversation_id")
    if conversation_id is not None and (not isinstance(conversation_id,str) or len(conversation_id)>80): raise ContractError("conversation_id must be at most 80 characters")
    return DraftRequest(case_id,message,order_id,locale,conversation_id)

def validate_draft_shape(value: dict) -> dict:
    required={"draft","evidence","needs_human_review","review_reasons"}
    if not isinstance(value,dict) or set(value)!=required: raise ContractError("Draft does not match the required output fields")
    if not isinstance(value["draft"],str) or len(value["draft"])>600: raise ContractError("draft must be text up to 600 characters")
    if not isinstance(value["evidence"],list): raise ContractError("evidence must be a list")
    for e in value["evidence"]:
        if not isinstance(e,dict) or set(e)!={"field","value"} or not isinstance(e["field"],str): raise ContractError("Each evidence item requires field and value")
    if not isinstance(value["needs_human_review"],bool): raise ContractError("needs_human_review must be boolean")
    if not isinstance(value["review_reasons"],list) or not all(isinstance(x,str) for x in value["review_reasons"]): raise ContractError("review_reasons must be a list of strings")
    return value
