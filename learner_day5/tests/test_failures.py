import unittest
from src.model import DeterministicModel
from src.source_tool import ReadOnlyOrderLookup
from src.service import DraftService

class FailureTests(unittest.TestCase):
 def test_wrong_but_well_formed_evidence_is_rejected(self):
  service=DraftService(DeterministicModel(wrong_claim=True),ReadOnlyOrderLookup())
  with self.assertRaisesRegex(ValueError,"Evidence mismatch"):
   service.create({"case_id":"C1","customer_message":"Can I get refund?","order_id":"ORD-1042"})
 def test_incomplete_output_fails_safely(self):
  service=DraftService(DeterministicModel(status="incomplete"),ReadOnlyOrderLookup())
  with self.assertRaisesRegex(RuntimeError,"incomplete"):
   service.create({"case_id":"C1","customer_message":"Help","order_id":"ORD-1042"})

if __name__=="__main__":unittest.main()
