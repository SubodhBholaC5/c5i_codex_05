import uuid
from .cache import RequestCache
from .models import DraftResponse, ContractError
from .semantic_validation import validate_evidence
from .validation import validate_draft_shape, validate_request

class DraftService:
    def __init__(self,model,tool,cache=None): self.model=model; self.tool=tool; self.cache=cache or RequestCache()
    def create(self,payload,user_id="demo-user",use_cache=True):
        request=validate_request(payload)
        order=self.tool(request.order_id) if request.order_id else None
        key=self.cache.key(user_id,request,self.tool.version,"prompt-v1",type(self.model).__name__)
        result=self.cache.get(key) if use_cache else None
        if result is None:
            result=self.model.generate(request,order)
            if result.status!="completed": raise RuntimeError(f"Model response ended with status: {result.status}")
            shaped=validate_draft_shape(result.output)
            validate_evidence(shaped,order)
            self.cache.set(key,result)
        else:
            shaped=validate_draft_shape(result.output)
            validate_evidence(shaped,order)
        return DraftResponse(request.case_id,shaped["draft"],shaped["evidence"],shaped["needs_human_review"],shaped["review_reasons"],{"input_tokens":result.input_tokens,"output_tokens":result.output_tokens,"estimated_cost_usd":round(result.cost_usd,8)},uuid.uuid4().hex[:12])
