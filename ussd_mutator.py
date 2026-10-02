import copy

# Expanded Mutation Vectors
FUZZ_VECTORS = {
    # Structural & Basic Nulls
    "null_value": None,
    "empty_string": "",
    
    # Boundary & Type Mismatches
    "negative_int": -1,
    "large_negative_int": -999999999,
    "zero_value": 0,
    "boolean_true": True,
    
    # Strings & Encodings
    "unicode_non_ascii": "Tëst_Rôutë_ñ_中文_🔥",
    "overflow_string": "A" * 2048,
    "sql_injection_pattern": "' OR '1'='1",
    "xss_pattern": "<script>alert(1)</script>",
    "format_string": "%s%x%d%n",
    
    # Formatting / Special Chars
    "whitespace_only": "   \t\n   ",
    "control_characters": "\x00\x1b\x07",
}

def mutate_ussd_payload(base_payload: dict):
    mutations = []
    
    # 1. Mutate root-level parameters
    for root_key in ["languageCode", "sessionIdentifier", "journeyIdentifier"]:
        if root_key in base_payload:
            for v_name, v_val in FUZZ_VECTORS.items():
                mutated = copy.deepcopy(base_payload)
                mutated[root_key] = v_val
                mutations.append({
                    "target": f"root.{root_key}",
                    "type": v_name,
                    "payload": mutated
                })

    # 2. Mutate key-value pairs inside the 'arguments' array
    args = base_payload.get("arguments", [])
    for idx, arg in enumerate(args):
        key_name = arg.get("key", {}).get("value", f"arg_{idx}")
        for v_name, v_val in FUZZ_VECTORS.items():
            mutated = copy.deepcopy(base_payload)
            mutated["arguments"][idx]["value"]["value"] = v_val
            mutations.append({
                "target": f"arguments[{key_name}]",
                "type": v_name,
                "payload": mutated
            })

    # 3. Array Boundary Mutation: Oversized arguments array
    oversized_payload = copy.deepcopy(base_payload)
    oversized_payload["arguments"] = args * 50  # Duplicate items to test payload size boundaries
    mutations.append({
        "target": "root.arguments",
        "type": "array_overflow",
        "payload": oversized_payload
    })

    # 4. Array Boundary Mutation: Empty arguments array
    empty_args_payload = copy.deepcopy(base_payload)
    empty_args_payload["arguments"] = []
    mutations.append({
        "target": "root.arguments",
        "type": "empty_array",
        "payload": empty_args_payload
    })

    return mutations