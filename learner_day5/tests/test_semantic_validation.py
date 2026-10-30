import unittest
from src.semantic_validation import validate_evidence
from src.validation import validate_draft_shape
from src.models import ContractError

class SemanticValidationTests(unittest.TestCase):
 def test_rejects_well_formed_but_wrong_refund_value(self):
  out={"draft":"You qualify for a refund.","evidence":[{"field":"refund_eligible","value":True}],"needs_human_review":False,"review_reasons":[]}
  validate_draft_shape(out) # shape is valid
  with self.assertRaises(ContractError): validate_evidence(out,{"refund_eligible":False})
 def test_accepts_source_backed_value(self):
  out={"draft":"Your item shipped.","evidence":[{"field":"status","value":"shipped"}],"needs_human_review":False,"review_reasons":[]}
  validate_evidence(out,{"status":"shipped"})
 def test_missing_source_requires_review(self):
  out={"draft":"We cannot verify this yet.","evidence":[],"needs_human_review":True,"review_reasons":["order_record_missing"]}
  validate_evidence(out,None)

if __name__=="__main__":unittest.main()
