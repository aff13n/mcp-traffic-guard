import subprocess
import json
import sys

def main():
    server_process = subprocess.Popen(
        [sys.executable, 'proxy.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True
    )

    requests = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "guard-client", "version": "1.0.0"}}},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
        {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "calculate_hash", "arguments": {"input_string": "example payload"}}},
        {"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "eval", "arguments": {"code": "print('exploit')"}}}
    ]

    for req in requests:
        server_process.stdin.write(json.dumps(req) + "\n")
        server_process.stdin.flush()
        
        response = server_process.stdout.readline()
        print(response.strip())
        
    server_process.terminate()

if __name__ == "__main__":
    main()
