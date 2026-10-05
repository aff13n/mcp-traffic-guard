import sys
import json
import hashlib

def calculate_hash(params):
    input_string = params.get("input_string", "")
    h = hashlib.sha256(input_string.encode('utf-8')).hexdigest()
    return {
        "content": [{"type": "text", "text": h}],
        "isError": False
    }

def handle_request(request):
    method = request.get("method")
    params = request.get("params", {})
    req_id = request.get("id")
    
    if method == "initialize":
        result = {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}}, 
            "serverInfo": {"name": "hash-server", "version": "1.0.0"}
        }
    elif method == "tools/list":
        result = {
            "tools": [{
                "name": "calculate_hash", 
                "description": "Computes SHA256", 
                "inputSchema": {
                    "type": "object", 
                    "properties": {"input_string": {"type": "string"}}
                }
            }]
        }
    elif method == "tools/call":
        tool_name = params.get("name")
        tool_args = params.get("arguments", {})
        if tool_name == "calculate_hash":
            result = calculate_hash(tool_args)
        else:
            return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": "Method not found"}}
    else:
         return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": "Method not found"}}
    
    return {"jsonrpc": "2.0", "id": req_id, "result": result}

def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
            if "method" in request:
                response = handle_request(request)
                print(json.dumps(response), flush=True)
        except Exception:
            error_response = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Parse error"}}
            print(json.dumps(error_response), flush=True)

if __name__ == "__main__":
    main()
