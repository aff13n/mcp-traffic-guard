import sys
import json
import logging
import subprocess
import threading
from datetime import datetime, timezone
import hashlib

# Setup JSON telemetry logger
logger = logging.getLogger('telemetry')
logger.setLevel(logging.INFO)
handler = logging.FileHandler('traffic.log')
handler.setFormatter(logging.Formatter('%(message)s'))
logger.addHandler(handler)

BLOCKED_TOOLS = {"eval", "system_exec"}

def log_telemetry(req, disposition):
    """Logs structured telemetry in JSON Lines format with ISO-8601 timestamps."""
    telemetry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "disposition": disposition,
        "method": req.get("method", "unknown"),
        "id": req.get("id"),
        "tool_name": None,
        "params_hash": None,
    }
    
    if req.get("method") == "tools/call":
        params = req.get("params", {})
        telemetry["tool_name"] = params.get("name")
        # Hash arguments for telemetry without leaking sensitive PII/secrets
        args_str = json.dumps(params.get("arguments", {}), sort_keys=True).encode('utf-8')
        telemetry["params_hash"] = hashlib.sha256(args_str).hexdigest()
        
    logger.info(json.dumps(telemetry))

def relay_stdout(process):
    """Relays server stdout to proxy stdout asynchronously to prevent deadlocks."""
    for line in process.stdout:
        sys.stdout.write(line)
        sys.stdout.flush()

def main():
    server_process = subprocess.Popen(
        [sys.executable, 'server.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True,
        bufsize=1
    )

    # Start asynchronous relay of server responses
    stdout_thread = threading.Thread(target=relay_stdout, args=(server_process,), daemon=True)
    stdout_thread.start()

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
            
        try:
            req = json.loads(line)
            
            # Fail-closed validation: Must be a valid JSON-RPC 2.0 object
            if not isinstance(req, dict) or req.get("jsonrpc") != "2.0" or "method" not in req:
                log_telemetry(req if isinstance(req, dict) else {}, "DROPPED_MALFORMED")
                # Don't forward malformed messages
                continue
                
            method = req.get("method")
            params = req.get("params", {})

            # Policy Gate
            if method == "tools/call" and params.get("name") in BLOCKED_TOOLS:
                log_telemetry(req, "BLOCKED")
                error_resp = {
                    "jsonrpc": "2.0", 
                    "id": req.get("id"), 
                    "error": {"code": -32601, "message": "Method not found (Blocked by Security Policy)"}
                }
                print(json.dumps(error_resp), flush=True)
                continue
                
            # Allow and forward
            log_telemetry(req, "ALLOWED")
            server_process.stdin.write(line + "\n")
            server_process.stdin.flush()
            
        except json.JSONDecodeError:
            # Drop entirely on parse failure (Fail-closed)
            pass
            
    server_process.stdin.close()
    server_process.wait()

if __name__ == "__main__":
    main()
