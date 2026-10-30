import statistics,time
from .models import DraftRequest
from .source_tool import ReadOnlyOrderLookup
from .model import DeterministicModel
from .cache import RequestCache
from .service import DraftService

PAYLOAD={"case_id":"CASE-1","customer_message":"Where is my package?","order_id":"ORD-1042"}
def run(n=100,use_cache=True):
 tool=ReadOnlyOrderLookup(); model=DeterministicModel(); cache=RequestCache(); service=DraftService(model,tool,cache); values=[]
 start=time.perf_counter()
 for _ in range(n):
  t=time.perf_counter();service.create(PAYLOAD,user_id="benchmark-user",use_cache=use_cache);values.append((time.perf_counter()-t)*1000)
 elapsed=(time.perf_counter()-start)*1000
 ordered=sorted(values)
 p95=ordered[min(len(ordered)-1,int(.95*len(ordered)))]
 calls=model.calls
 sample_tokens=max(1,(len(PAYLOAD["customer_message"])+len(str(tool(PAYLOAD["order_id"])) )+20)//4)
 output_tokens=30
 cost_per_call=sample_tokens/1_000_000*1.0+output_tokens/1_000_000*4.0
 return {"requests":n,"p50_ms":round(statistics.median(values),4),"p95_ms":round(p95,4),"total_ms":round(elapsed,4),"model_calls":calls,"cache_hits":cache.hits,"cache_misses":cache.misses,"input_tokens_estimate_per_model_call":sample_tokens,"output_tokens_estimate_per_model_call":output_tokens,"estimated_model_cost_usd":round(calls*cost_per_call,8)}
if __name__=="__main__":
 for enabled in (False,True): print(("CACHED" if enabled else "UNCACHED"),run(use_cache=enabled))
