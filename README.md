# mcp-traffic-guard

An intercepting proxy for Model Context Protocol (MCP) servers.

## Architecture

```
+------------+       JSON-RPC (stdio)      +------------+        JSON-RPC (stdio)      +------------+
|            | --------------------------> |            | ---------------------------> |            |
| client.py  |                             |  proxy.py  |                              | server.py  |
|            | <-------------------------- |            | <--------------------------- |            |
+------------+                             +------------+                              +------------+
                                                 | (Logs traffic & enforces policy)
                                                 v
                                            traffic.log
```

## Security Model
Prevents unmonitored agent tool execution. The proxy sits between the client and server to log all traffic and apply a blocklist against risky execution tools (e.g. `eval`, `system_exec`).

## Usage
1. **Setup**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Run Tests (via Proxy)**:
   ```bash
   python3 client.py
   ```

3. **Bypass Proxy**:
   To test directly against the server, update `client.py`'s subprocess target:
   ```python
   server_process = subprocess.Popen([sys.executable, 'server.py'], ...)
   ```
