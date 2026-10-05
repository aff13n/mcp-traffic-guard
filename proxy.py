import sys
import json
import logging
import subprocess

logging.basicConfig(filename='traffic.log', level=logging.INFO, format='%(asctime)s - %(message)s')
BLOCKED_TOOLS = ["eval", "system_exec"]

def main():
    server_process = subprocess.Popen(
        [sys.executable, 'server.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True
    )

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
            
        try:
            req = json.loads(line)
            method = req.get("method")
            params = req.get("params", {})
            
            logging.info(f"method: {method}, params: {json.dumps(params)}")

            if method == "tools/call" and params.get("name") in BLOCKED_TOOLS:
                error_resp = {"jsonrpc": "2.0", "id": req.get("id", None), "error": {"code": -32601, "message": "Method not found (Blocked)"}}
                print(json.dumps(error_resp), flush=True)
                continue
                
            server_process.stdin.write(line + "\n")
            server_process.stdin.flush()
            
            response = server_process.stdout.readline()
            print(response.strip(), flush=True)
            
        except json.JSONDecodeError:
            pass
            
    server_process.terminate()

if __name__ == "__main__":
    main()
