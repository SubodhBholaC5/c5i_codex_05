import unittest
from src.validation import validate_request,validate_draft_shape
from src.models import ContractError

class ContractTests(unittest.TestCase):
 def test_valid_request_defaults_locale(self): self.assertEqual(validate_request({"case_id":"C1","customer_message":"Help"}).locale,"en")
 def test_rejects_oversize_message(self):
  with self.assertRaises(ContractError): validate_request({"case_id":"C1","customer_message":"x"*2001})
 def test_rejects_unknown_field(self):
  with self.assertRaises(ContractError): validate_request({"case_id":"C1","customer_message":"Help","send_now":True})
 def test_schema_shape_does_not_validate_truth(self):
  out={"draft":"Done","evidence":[{"field":"refund_eligible","value":True}],"needs_human_review":False,"review_reasons":[]}
  self.assertEqual(validate_draft_shape(out),out)
  # Source consistency is tested separately in test_semantic_validation.py

if __name__=="__main__":unittest.main()
