import copy

# Dictionary of standard fuzzing test vectors categorized by intention
FUZZ_VECTORS = {
    "null_value": None,
    "empty_string": "",
    "type_mismatch_int_as_str": "999999999",
    "type_mismatch_str_as_int": -12345,
    "boolean_flip": True,
    "boundary_overflow": "A" * 1000,
    "special_chars": "<script>alert(1)</script>' OR '1'='1"
}

def generate_mutated_payloads(base_payload: dict):
    """
    Takes a valid JSON base payload and generates a list of mutated copies.
    Each copy alters exactly ONE field at a time to isolate which input broke the API.
    """
    mutated_samples = []

    for key in base_payload.keys():
        for vector_name, value in FUZZ_VECTORS.items():
            # Deep copy to avoid modifying the original dictionary across iterations
            mutated = copy.deepcopy(base_payload)
            mutated[key] = value
            
            mutated_samples.append({
                "target_field": key,
                "mutation_type": vector_name,
                "payload": mutated
            })

    return mutated_samples

if __name__ == "__main__":
    # Example baseline valid payload for creating a ticket bouquet
    sample_payload = {
        "name": "VIP Pass",
        "price": 15000,
        "quantity": 100,
        "active": True
    }

    mutations = generate_mutated_payloads(sample_payload)
    print(f"[*] Generated {len(mutations)} mutated test payloads from 1 base sample.\n")

    # Preview the first 3 generated mutations
    for i, m in enumerate(mutations[:3], 1):
        print(f"--- Mutation {i}: Field '{m['target_field']}' ({m['mutation_type']}) ---")
        print(m["payload"])
        print()