# tagentacle-py-inferencemux

**InferenceMux SDK** — Inference trigger mechanism for Tagentacle agent nodes.

## Overview

| Component | Description |
|-----------|-------------|
| `InferenceMux` | Controls when to infer: IDLE/BUSY state machine + followup queue (~50 lines) |

> **Q27 restructuring**: `Inbox` moved to `tagentacle-py-core`. This package focuses solely on the inference multiplexer.

### Design Principles

- **Mechanism, not policy** — InferenceMux triggers; the agent node decides what to do
- **No topic names hardcoded** — SDK doesn't know any specific topic
- **< 100 lines** — if it exceeds this, policies are leaking in

### Message Flow

```
Bus topic callback → Inbox.push(topic, msg)   (in tagentacle-py-core)
                       └─ mode=followup → signal InferenceMux

InferenceMux.trigger() → _agentic_loop() reads Inbox.drain()
```

## Architecture Context

```
tagentacle-py-core:          Node, LifecycleNode, Inbox (kernel-level)
tagentacle-py-mcp:           BusMCPNode, InboxMCP (MCP layer)
tagentacle-py-inferencemux:  InferenceMux (inference trigger)  ← this
tagentacle-py-tacl:          TACLAuthority, TACLMiddleware (access control)
```

## Status

**Phase 1 — full-stack-v1**: Package created. Q27 restructuring in progress.

→ [Project board](https://github.com/orgs/Tagentacle/projects/1)

## License

MIT
