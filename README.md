# mcp-traffic-guard

An intercepting proxy for Model Context Protocol (MCP) servers designed for security researchers and LLM red teams.

## Architecture

```
+------------+       JSON-RPC (stdio)      +------------+        JSON-RPC (stdio)      +------------+
|            | --------------------------> |            | ---------------------------> |            |
| LLM Agent  |                             |  proxy.py  |                              | server.py  |
| (Client)   | <-------------------------- |            | <--------------------------- | (Tools)    |
+------------+                             +------------+                              +------------+
                                                 | (Telemetry & Policy Gate)
                                                 v
                                            traffic.log (JSONL)
```

## Security Threat Model

This architecture addresses specific risks in the OWASP Top 10 for LLMs, specifically:
- **LLM08: Excessive Agency**: Prevents unmonitored or autonomous tool execution by acting as a strict policy gate.
- **LLM02: Insecure Output Handling / Indirect Prompt Injection**: If a downstream tool response contains a malicious payload that compromises the agent (e.g., instructing the agent to run `eval` or `system_exec`), this proxy catches and drops the resulting unauthorized execution attempts.

### Key Security Features:
1. **Asynchronous Protocol Adherence**: Handles `stdio` multiplexing safely via threaded execution, preventing JSON-RPC buffering deadlocks.
2. **Fail-Closed Design**: Messages that are malformed or fail to strictly match JSON-RPC 2.0 specifications are dropped rather than forwarded to the sensitive execution environment.
3. **Structured Telemetry**: Generates ISO-8601 compliant JSON Lines (JSONL) logs. Tool arguments are cryptographically hashed (SHA-256) to provide auditability without leaking sensitive PII or secrets to the log sink.

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
