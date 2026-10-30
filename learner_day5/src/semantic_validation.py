from .models import ContractError

def validate_evidence(output: dict, source_record: dict | None) -> dict:
    """Validate truth against source of record, independently of JSON shape."""
    if not output["evidence"] and source_record is not None:
        raise ContractError("A sourced order response must include evidence")
    allowed={"status","estimated_delivery","refund_eligible"}
    for item in output["evidence"]:
        field=item["field"]
        if field not in allowed: raise ContractError(f"Unsupported evidence field: {field}")
        if source_record is None or item["value"] != source_record.get(field):
            raise ContractError(f"Evidence mismatch for {field}")
    if source_record is None and not output["needs_human_review"]:
        raise ContractError("Missing source requires human review")
    return output
