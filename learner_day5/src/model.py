from dataclasses import dataclass

@dataclass
class ModelResult:
    output: dict
    input_tokens: int
    output_tokens: int
    latency_ms: float
    cost_usd: float
    status: str="completed"

class DeterministicModel:
    """Local model stand-in; replace with live Responses API in optional extension."""
    def __init__(self, wrong_claim=False, status="completed"):
        self.calls=0; self.wrong_claim=wrong_claim; self.status=status
    def generate(self, request, order):
        import time
        self.calls+=1; start=time.perf_counter()
        if self.status!="completed": return ModelResult({},100,0,(time.perf_counter()-start)*1000,0,self.status)
        evidence=[]; review=False; reasons=[]
        if order is None:
            draft="I could not verify the order details from the information available. A support agent will review this case."
            review=True; reasons=["order_record_missing"]
        else:
            evidence=[{"field":"status","value":order["status"]}]
            if order.get("estimated_delivery"):
                evidence.append({"field":"estimated_delivery","value":order["estimated_delivery"]})
            eligible=order.get("refund_eligible")
            if eligible is not None:
                evidence.append({"field":"refund_eligible","value":eligible})
            if self.wrong_claim:
                evidence[-1]["value"]=not eligible # Valid bool and correct shape, but contradicts source.
            if order["status"]=="shipped":
                draft=f"Your order is on its way, with estimated delivery on {order['estimated_delivery']}. I’m sorry for the wait."
            elif order["status"]=="delivered": draft="Your order shows as delivered. I’m sorry for the trouble; a support agent can review the return options with you."
            else:
                draft="Your order is being prepared. I’ll ask a support agent to check the latest delivery estimate."
                review=True;reasons=["delivery_estimate_unavailable"]
        elapsed=(time.perf_counter()-start)*1000
        input_tokens=max(1,(len(request.customer_message)+len(str(order))+20)//4)
        output_tokens=max(1,len(draft)//4)
        # Teaching-only rate card: $1 / 1M input, $4 / 1M output tokens.
        cost=input_tokens/1_000_000*1.0+output_tokens/1_000_000*4.0
        return ModelResult({"draft":draft,"evidence":evidence,"needs_human_review":review,"review_reasons":reasons},input_tokens,output_tokens,elapsed,cost)
