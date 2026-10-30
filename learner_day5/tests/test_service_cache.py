import unittest
from src.model import DeterministicModel
from src.source_tool import ReadOnlyOrderLookup
from src.service import DraftService

class ServiceCacheTests(unittest.TestCase):
 def setUp(self): self.model=DeterministicModel();self.service=DraftService(self.model,ReadOnlyOrderLookup())
 def payload(self): return {"case_id":"C1","customer_message":"Where is my order?","order_id":"ORD-1042"}
 def test_repeat_same_user_request_uses_cache(self):
  self.service.create(self.payload(),"u1");self.service.create(self.payload(),"u1");self.assertEqual(self.model.calls,1)
 def test_cache_isolated_by_user(self):
  self.service.create(self.payload(),"u1");self.service.create(self.payload(),"u2");self.assertEqual(self.model.calls,2)
 def test_uncached_mode_measures_each_model_call(self):
  self.service.create(self.payload(),"u1",use_cache=False);self.service.create(self.payload(),"u1",use_cache=False);self.assertEqual(self.model.calls,2)

if __name__=="__main__":unittest.main()
