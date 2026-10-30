import hashlib, json

class RequestCache:
    """Process-local demo cache; key includes user, normalized request and versions."""
    def __init__(self): self._values={}; self.hits=0; self.misses=0
    def key(self,user_id,request,source_version,prompt_version,model_name):
        payload={"user_id":user_id,"case_id":request.case_id,"message":request.customer_message.strip(),"order_id":request.order_id,"locale":request.locale,"conversation_id":request.conversation_id,"source_version":source_version,"prompt_version":prompt_version,"model":model_name}
        return hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()
    def get(self,key):
        if key in self._values: self.hits+=1; return self._values[key]
        self.misses+=1; return None
    def set(self,key,value): self._values[key]=value
