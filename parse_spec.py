import json

def load_and_parse_spec(filepath="empayit_swagger.json"):
    with open(filepath, "r") as f:
        spec = json.load(f)

    paths = spec.get("paths", {})
    print(f"[*] Total endpoints found in OpenAPI spec: {len(paths)}\n")

    endpoint_summary = []

    for path, methods in paths.items():
        for method, details in methods.items():
            # Skip non-HTTP keys like parameters or summary at path level
            if method.lower() not in ['get', 'post', 'put', 'delete', 'patch']:
                continue
            
            operation_id = details.get("operationId", "N/A")
            has_body = "requestBody" in details
            
            endpoint_summary.append({
                "path": path,
                "method": method.upper(),
                "operationId": operation_id,
                "has_body": has_body
            })

    # Print out the first 5 endpoints as a preview
    print(f"{'METHOD':<8} | {'HAS BODY':<10} | {'PATH'}")
    print("-" * 60)
    for ep in endpoint_summary[:10]:
        print(f"{ep['method']:<8} | {str(ep['has_body']):<10} | {ep['path']}")

    return endpoint_summary

if __name__ == "__main__":
    load_and_parse_spec()