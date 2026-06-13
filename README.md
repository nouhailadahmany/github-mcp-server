# GitHub Prod MCP

Production-ready GitHub MCP server implemented in Python, based on the official GitHub REST API documentation at `https://docs.github.com/en/rest`.

## Features

- MCP stdio server for GitHub operations
- REST API wrapper exposing the same tools
- POST-only tool endpoints
- Request-body-only inputs for tool APIs
- Centralized validation with Pydantic models
- GitHub API version header support
- Timeout handling and normalized API errors
- Shared service layer for MCP and REST parity

## Implemented tools

- `get_authenticated_user`
- `create_repository`
- `get_repository`
- `get_repository_details`
- `list_branches`
- `get_branch`
- `list_repository_files`
- `get_file_content`
- `search_repositories`
- `search_code`
- `search_issues`
- `list_issues`
- `get_issue`
- `create_issue`
- `update_issue`
- `create_issue_comment`
- `list_pull_requests`
- `get_pull_request`
- `create_pull_request`
- `merge_pull_request`
- `get_commit`
- `compare_commits`
- `create_or_update_file`
- `delete_file`
- `create_repository_dispatch`
- `trigger_workflow_dispatch`
- `list_workflow_runs`

## Project structure

- `src/github_prod_mcp/main.py` - MCP stdio server
- `src/github_prod_mcp/rest_api.py` - REST API wrapper
- `src/github_prod_mcp/github_api.py` - GitHub REST client
- `src/github_prod_mcp/service.py` - shared business layer
- `src/github_prod_mcp/models.py` - request and response schemas
- `src/github_prod_mcp/config.py` - environment-driven settings

## Requirements

- Python 3.10+
- A GitHub token with the scopes required for the operations you plan to use

## Setup

### 1. Create a virtual environment

PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
python -m pip install --upgrade pip
python -m pip install -e .
```

### 3. Configure environment

Copy [`.env.example`](.env.example) to `.env` and set your token:

```env
GITHUB_TOKEN=ghp_your_token_here
GITHUB_API_BASE_URL=https://api.github.com
GITHUB_API_VERSION=2022-11-28
GITHUB_USER_AGENT=github-prod-mcp/0.1.0
GITHUB_TIMEOUT_SECONDS=30
REST_HOST=127.0.0.1
REST_PORT=8080
LOG_LEVEL=INFO
```

## Run the MCP server

```powershell
python -m github_prod_mcp.main
```

## Run the REST API

```powershell
python -m github_prod_mcp.rest_api
```

REST docs will be available at:

- `http://127.0.0.1:8080/docs`
- `http://127.0.0.1:8080/openapi.json`

## REST API design rule

All tool endpoints are exposed as `POST` endpoints under `/tools/...`.

For tool execution:
- no path variables
- no query variables
- inputs are passed in the JSON request body only

Examples:

### Get repository

```http
POST /tools/get_repository
Content-Type: application/json

{
  "owner": "octocat",
  "repo": "Hello-World"
}
```

### Get repository details

```http
POST /tools/get_repository_details
Content-Type: application/json

{
  "owner": "octocat",
  "repo": "Hello-World",
  "include_branches": true,
  "include_root_files": true,
  "include_readme": false
}
```

### List repository files

```http
POST /tools/list_repository_files
Content-Type: application/json

{
  "owner": "octocat",
  "repo": "Hello-World",
  "path": "",
  "ref": "main"
}
```

### Get file content metadata

```http
POST /tools/get_file_content
Content-Type: application/json

{
  "owner": "octocat",
  "repo": "Hello-World",
  "path": "README.md",
  "ref": "main"
}
```

### Create issue

```http
POST /tools/create_issue
Content-Type: application/json

{
  "owner": "octocat",
  "repo": "Hello-World",
  "title": "Bug report",
  "body": "Something is broken"
}
```

### Trigger workflow dispatch

```http
POST /tools/trigger_workflow_dispatch
Content-Type: application/json

{
  "owner": "octocat",
  "repo": "Hello-World",
  "workflow_id": "ci.yml",
  "ref": "main",
  "inputs": {
    "environment": "prod"
  }
}
```

## MCP registration

Update [`.bob/mcp.json`](../.bob/mcp.json) so Bob can launch the stdio server.

Example configuration:

```json
{
  "mcpServers": {
    "github-prod-mcp": {
      "command": "python",
      "args": [
        "-m",
        "github_prod_mcp.main"
      ],
      "cwd": "c:/Users/abdenourChenouf/Documents/MCP-Github/github-prod-mcp",
      "env": {
        "GITHUB_TOKEN": "YOUR_GITHUB_TOKEN",
        "GITHUB_API_BASE_URL": "https://api.github.com",
        "GITHUB_API_VERSION": "2022-11-28",
        "GITHUB_USER_AGENT": "github-prod-mcp/0.1.0",
        "GITHUB_TIMEOUT_SECONDS": "30",
        "LOG_LEVEL": "INFO"
      },
      "disabled": false,
      "alwaysAllow": [],
      "disabledTools": []
    }
  }
}
```

## Production notes

- Use a fine-grained GitHub token with least privilege
- Rotate tokens regularly
- Keep `.env` out of source control
- Run the REST API behind a reverse proxy for TLS and access control
- Add request authentication in front of the REST API before internet exposure
- Tune timeout and logging for your environment
- Add tests before deploying to shared environments

## Official API basis

This implementation follows GitHub REST API conventions including:
- `Accept: application/vnd.github+json`
- `Authorization: Bearer <token>`
- `X-GitHub-Api-Version: 2022-11-28`

Reference:
- `https://docs.github.com/en/rest`