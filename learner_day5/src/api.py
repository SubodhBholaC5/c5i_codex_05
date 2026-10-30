"""Framework-neutral endpoint adapter for classroom use."""
from .model import DeterministicModel
from .service import DraftService
from .source_tool import ReadOnlyOrderLookup
from .models import ContractError

_service=DraftService(DeterministicModel(),ReadOnlyOrderLookup())

def post_reply_draft(payload,user_id="demo-user"):
    try:
        result=_service.create(payload,user_id)
        return 200,result.__dict__
    except ContractError as e: return 400,{"error":"invalid_request_or_output","message":str(e)}
    except RuntimeError: return 503,{"error":"generation_unavailable","message":"Draft could not be generated. Please retry or route to an agent."}
