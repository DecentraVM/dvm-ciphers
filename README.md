DVM Execution Engine
Serverless Code Interpretation for AI Agents

DVM (Distributed Virtual Machine) is a decentralized platform designed for AI agent code execution.
This Docker-based execution engine provides secure, isolated, and scalable code execution with full
AWS Lambda compatibility.

FEATURES
- Multi-language support: Python, TypeScript, PHP
- AWS Lambda compatible runtime
- Secure containerized execution
- Structured input and output
- Real-time execution
- Cloud-ready design

ARCHITECTURE
The DVM runner operates as a Docker container exposing an AWS Lambda-compatible API endpoint.
This allows deployment on any infrastructure, horizontal scaling, and seamless Lambda workflow integration.

QUICK START (DOCKER)

Build the container:
docker build -t dvm-runner .

Run the container:
docker run -p 9000:8080 dvm-runner

Test execution:
curl -X POST http://localhost:9000/2015-03-31/functions/function/invocations \
-H "Content-Type: application/json" \
-d '{"language":"python","code":"print(\"Hello, DVM!\")"}'

USING PODMAN

podman build -t dvm-runner .
podman run -p 9000:8080 dvm-runner

API USAGE

Basic execution:
curl -X POST http://localhost:9000/2015-03-31/functions/function/invocations \
-H "Content-Type: application/json" \
-d '{"language":"python","code":"print(\"hello world\")"}'

Execution with input:
curl -X POST http://localhost:9000/2015-03-31/functions/function/invocations \
-H "Content-Type: application/json" \
-d '{"language":"python","input":{"a":1,"b":2},"code":"print(a + b)"}'

Structured output:
curl -X POST http://localhost:9000/2015-03-31/functions/function/invocations \
-H "Content-Type: application/json" \
-d '{"language":"python","input":{"a":1,"b":2},"code":"output = {\"result\": a + b}"}'

Environment variables:
curl -X POST http://localhost:9000/2015-03-31/functions/function/invocations \
-H "Content-Type: application/json" \
-d '{"language":"python","input":{"a":1,"b":2},"env":{"c":"4"},"code":"output = {\"result\": a + b + int(os.environ[\"c\"])}"}'

REQUEST FORMAT
{
  "language": "python | typescript | php",
  "code": "your_code_here",
  "input": {
    "key": "value"
  },
  "env": {
    "key": "value"
  }
}

SUPPORTED LANGUAGES
- Python
- TypeScript
- PHP

LICENSE
Part of the DVM ecosystem.
