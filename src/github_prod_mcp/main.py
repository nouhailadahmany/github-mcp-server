from __future__ import annotations

import json
import logging
import sys
from typing import Any, Callable

from github_prod_mcp.config import get_settings
from github_prod_mcp.github_api import GitHubApiClient, GitHubApiError
from github_prod_mcp.models import (
    AppendToFileRequest,
    BranchRequest,
    CompareCommitsRequest,
    CreateCommentRequest,
    CreateDispatchEventRequest,
    CreateIssueRequest,
    CreateRepositoryRequest,
    CreateOrUpdateFileRequest,
    CreatePullRequestRequest,
    DeleteFileRequest,
    FileContentRequest,
    GetCommitRequest,
    IssueIdentifierRequest,
    ListRepositoryFilesRequest,
    ListWorkflowRunsRequest,
    MergePullRequestRequest,
    OwnerRepoRequest,
    PullRequestIdentifierRequest,
    RepositoryDetailsRequest,
    SearchCodeRequest,
    SearchIssuesRequest,
    SearchRepositoriesRequest,
    TriggerWorkflowDispatchRequest,
    UpdateIssueRequest,
)
from github_prod_mcp.service import GitHubService


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
LOGGER = logging.getLogger("github_prod_mcp")


def _success_response(request_id: Any, result: Any) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def _error_response(request_id: Any, code: int, message: str, data: Any | None = None) -> dict[str, Any]:
    error: dict[str, Any] = {"code": code, "message": message}
    if data is not None:
        error["data"] = data
    return {"jsonrpc": "2.0", "id": request_id, "error": error}


def _tool_result(payload: Any) -> dict[str, Any]:
    return {
        "content": [
            {
                "type": "text",
                "text": json.dumps(payload, indent=2, ensure_ascii=False),
            }
        ]
    }


def _build_tools() -> list[dict[str, Any]]:
    return [
        {"name": "get_authenticated_user", "description": "Get the authenticated GitHub user", "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False}},
        {"name": "create_repository", "description": "Create a repository for the authenticated user", "inputSchema": {"type": "object", "properties": {"name": {"type": "string"}, "description": {"type": "string"}, "homepage": {"type": "string"}, "private": {"type": "boolean"}, "has_issues": {"type": "boolean"}, "has_projects": {"type": "boolean"}, "has_wiki": {"type": "boolean"}, "auto_init": {"type": "boolean"}, "gitignore_template": {"type": "string"}, "license_template": {"type": "string"}}, "required": ["name"], "additionalProperties": False}},
        {"name": "get_repository", "description": "Get repository metadata", "inputSchema": {"type": "object", "properties": {"owner": {"type": "string"}, "repo": {"type": "string"}}, "required": ["owner", "repo"], "additionalProperties": False}},
        {"name": "list_branches", "description": "List repository branches", "inputSchema": {"type": "object", "properties": {"owner": {"type": "string"}, "repo": {"type": "string"}}, "required": ["owner", "repo"], "additionalProperties": False}},
        {"name": "get_branch", "description": "Get a branch by name", "inputSchema": {"type": "object", "properties": {"owner": {"type": "string"}, "repo": {"type": "string"}, "branch": {"type": "string"}}, "required": ["owner", "repo", "branch"], "additionalProperties": False}},
        {"name": "get_repository_details", "description": "Get repository details including optional branches, root files, and README metadata", "inputSchema": {"type": "object", "properties": {"owner": {"type": "string"}, "repo": {"type": "string"}, "include_branches": {"type": "boolean"}, "include_root_files": {"type": "boolean"}, "include_readme": {"type": "boolean"}}, "required": ["owner", "repo"], "additionalProperties": False}},
        {"name": "list_repository_files", "description": "List repository files or directory contents", "inputSchema": {"type": "object", "properties": {"owner": {"type": "string"}, "repo": {"type": "string"}, "path": {"type": "string"}, "ref": {"type": "string"}}, "required": ["owner", "repo"], "additionalProperties": False}},
        {"name": "get_file_content", "description": "Get repository file content metadata", "inputSchema": {"type": "object", "properties": {"owner": {"type": "string"}, "repo": {"type": "string"}, "path": {"type": "string"}, "ref": {"type": "string"}}, "required": ["owner", "repo", "path"], "additionalProperties": False}},
        {"name": "search_repositories", "description": "Search repositories", "inputSchema": {"type": "object", "properties": {"query": {"type": "string"}, "sort": {"type": "string"}, "order": {"type": "string"}, "per_page": {"type": "integer"}, "page": {"type": "integer"}}, "required": ["query"], "additionalProperties": False}},
        {"name": "search_code", "description": "Search code", "inputSchema": {"type": "object", "properties": {"query": {"type": "string"}, "sort": {"type": "string"}, "order": {"type": "string"}, "per_page": {"type": "integer"}, "page": {"type": "integer"}}, "required": ["query"], "additionalProperties": False}},
        {"name": "search_issues", "description": "Search issues and pull requests", "inputSchema": {"type": "object", "properties": {"query": {"type": "string"}, "sort": {"type": "string"}, "order": {"type": "string"}, "per_page": {"type": "integer"}, "page": {"type": "integer"}}, "required": ["query"], "additionalProperties": False}},
        {"name": "list_issues", "description": "List repository issues", "inputSchema": {"type": "object", "properties": {"owner": {"type": "string"}, "repo": {"type": "string"}}, "required": ["owner", "repo"], "additionalProperties": False}},
        {"name": "get_issue", "description": "Get an issue", "inputSchema": {"type": "object", "properties": {"owner": {"type": "string"}, "repo": {"type": "string"}, "issue_number": {"type": "integer"}}, "required": ["owner", "repo", "issue_number"], "additionalProperties": False}},
        {"name": "create_issue", "description": "Create an issue", "inputSchema": {"type": "object", "properties": {"owner": {"type": "string"}, "repo": {"type": "string"}, "title": {"type": "string"}, "body": {"type": "string"}, "assignees": {"type": "array", "items": {"type": "string"}}, "labels": {"type": "array", "items": {"type": "string"}}, "milestone": {"type": "integer"}}, "required": ["owner", "repo", "title"], "additionalProperties": False}},
        {"name": "update_issue", "description": "Update an issue", "inputSchema": {"type": "object", "properties": {"owner": {"type": "string"}, "repo": {"type": "string"}, "issue_number": {"type": "integer"}, "title": {"type": "string"}, "body": {"type": "string"}, "state": {"type": "string"}, "state_reason": {"type": "string"}, "assignees": {"type": "array", "items": {"type": "string"}}, "labels": {"type": "array", "items": {"type": "string"}}, "milestone": {"type": "integer"}}, "required": ["owner", "repo", "issue_number"], "additionalProperties": False}},
        {"name": "create_issue_comment", "description": "Create an issue comment", "inputSchema": {"type": "object", "properties": {"owner": {"type": "string"}, "repo": {"type": "string"}, "issue_number": {"type": "integer"}, "body": {"type": "string"}}, "required": ["owner", "repo", "issue_number", "body"], "additionalProperties": False}},
        {"name": "list_pull_requests", "description": "List pull requests", "inputSchema": {"type": "object", "properties": {"owner": {"type": "string"}, "repo": {"type": "string"}}, "required": ["owner", "repo"], "additionalProperties": False}},
        {"name": "get_pull_request", "description": "Get a pull request", "inputSchema": {"type": "object", "properties": {"owner": {"type": "string"}, "repo": {"type": "string"}, "pull_number": {"type": "integer"}}, "required": ["owner", "repo", "pull_number"], "additionalProperties": False}},
        {"name": "create_pull_request", "description": "Create a pull request", "inputSchema": {"type": "object", "properties": {"owner": {"type": "string"}, "repo": {"type": "string"}, "title": {"type": "string"}, "head": {"type": "string"}, "base": {"type": "string"}, "body": {"type": "string"}, "maintainer_can_modify": {"type": "boolean"}, "draft": {"type": "boolean"}}, "required": ["owner", "repo", "title", "head", "base"], "additionalProperties": False}},
        {"name": "merge_pull_request", "description": "Merge a pull request", "inputSchema": {"type": "object", "properties": {"owner": {"type": "string"}, "repo": {"type": "string"}, "pull_number": {"type": "integer"}, "commit_title": {"type": "string"}, "commit_message": {"type": "string"}, "merge_method": {"type": "string"}}, "required": ["owner", "repo", "pull_number"], "additionalProperties": False}},
        {"name": "get_commit", "description": "Get a commit", "inputSchema": {"type": "object", "properties": {"owner": {"type": "string"}, "repo": {"type": "string"}, "ref": {"type": "string"}}, "required": ["owner", "repo", "ref"], "additionalProperties": False}},
        {"name": "compare_commits", "description": "Compare commits", "inputSchema": {"type": "object", "properties": {"owner": {"type": "string"}, "repo": {"type": "string"}, "basehead": {"type": "string"}}, "required": ["owner", "repo", "basehead"], "additionalProperties": False}},
        {"name": "create_or_update_file", "description": "Create or update a repository file", "inputSchema": {"type": "object", "properties": {"owner": {"type": "string"}, "repo": {"type": "string"}, "path": {"type": "string"}, "message": {"type": "string"}, "content": {"type": "string"}, "branch": {"type": "string"}, "sha": {"type": "string"}, "committer": {"type": "object"}, "author": {"type": "object"}}, "required": ["owner", "repo", "path", "message", "content"], "additionalProperties": False}},
        {"name": "append_to_file", "description": "Append content to an existing repository file", "inputSchema": {"type": "object", "properties": {"owner": {"type": "string"}, "repo": {"type": "string"}, "path": {"type": "string"}, "content": {"type": "string"}, "message": {"type": "string"}, "branch": {"type": "string"}, "committer": {"type": "object"}, "author": {"type": "object"}}, "required": ["owner", "repo", "path", "content"], "additionalProperties": False}},
        {"name": "delete_file", "description": "Delete a repository file", "inputSchema": {"type": "object", "properties": {"owner": {"type": "string"}, "repo": {"type": "string"}, "path": {"type": "string"}, "message": {"type": "string"}, "sha": {"type": "string"}, "branch": {"type": "string"}, "committer": {"type": "object"}, "author": {"type": "object"}}, "required": ["owner", "repo", "path", "message", "sha"], "additionalProperties": False}},
        {"name": "create_repository_dispatch", "description": "Create a repository dispatch event", "inputSchema": {"type": "object", "properties": {"owner": {"type": "string"}, "repo": {"type": "string"}, "event_type": {"type": "string"}, "client_payload": {"type": "object"}}, "required": ["owner", "repo", "event_type"], "additionalProperties": False}},
        {"name": "trigger_workflow_dispatch", "description": "Trigger a workflow dispatch", "inputSchema": {"type": "object", "properties": {"owner": {"type": "string"}, "repo": {"type": "string"}, "workflow_id": {"type": "string"}, "ref": {"type": "string"}, "inputs": {"type": "object"}}, "required": ["owner", "repo", "workflow_id", "ref"], "additionalProperties": False}},
        {"name": "list_workflow_runs", "description": "List workflow runs", "inputSchema": {"type": "object", "properties": {"owner": {"type": "string"}, "repo": {"type": "string"}, "actor": {"type": "string"}, "branch": {"type": "string"}, "event": {"type": "string"}, "status": {"type": "string"}, "per_page": {"type": "integer"}, "page": {"type": "integer"}}, "required": ["owner", "repo"], "additionalProperties": False}},
    ]


def _dispatch_tool(service: GitHubService, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    handlers: dict[str, Callable[[dict[str, Any]], Any]] = {
        "get_authenticated_user": lambda _: service.get_authenticated_user(),
        "create_repository": lambda data: service.create_repository(CreateRepositoryRequest.model_validate(data)),
        "get_repository": lambda data: service.get_repository(OwnerRepoRequest.model_validate(data)),
        "list_branches": lambda data: service.list_branches(OwnerRepoRequest.model_validate(data)),
        "get_branch": lambda data: service.get_branch(BranchRequest.model_validate(data)),
        "get_repository_details": lambda data: service.get_repository_details(RepositoryDetailsRequest.model_validate(data)),
        "list_repository_files": lambda data: service.list_repository_files(ListRepositoryFilesRequest.model_validate(data)),
        "get_file_content": lambda data: service.get_file_content(FileContentRequest.model_validate(data)),
        "search_repositories": lambda data: service.search_repositories(SearchRepositoriesRequest.model_validate(data)),
        "search_code": lambda data: service.search_code(SearchCodeRequest.model_validate(data)),
        "search_issues": lambda data: service.search_issues(SearchIssuesRequest.model_validate(data)),
        "list_issues": lambda data: service.list_issues(OwnerRepoRequest.model_validate(data)),
        "get_issue": lambda data: service.get_issue(IssueIdentifierRequest.model_validate(data)),
        "create_issue": lambda data: service.create_issue(CreateIssueRequest.model_validate(data)),
        "update_issue": lambda data: service.update_issue(UpdateIssueRequest.model_validate(data)),
        "create_issue_comment": lambda data: service.create_issue_comment(CreateCommentRequest.model_validate(data)),
        "list_pull_requests": lambda data: service.list_pull_requests(OwnerRepoRequest.model_validate(data)),
        "get_pull_request": lambda data: service.get_pull_request(PullRequestIdentifierRequest.model_validate(data)),
        "create_pull_request": lambda data: service.create_pull_request(CreatePullRequestRequest.model_validate(data)),
        "merge_pull_request": lambda data: service.merge_pull_request(MergePullRequestRequest.model_validate(data)),
        "get_commit": lambda data: service.get_commit(GetCommitRequest.model_validate(data)),
        "compare_commits": lambda data: service.compare_commits(CompareCommitsRequest.model_validate(data)),
        "create_or_update_file": lambda data: service.create_or_update_file(CreateOrUpdateFileRequest.model_validate(data)),
        "append_to_file": lambda data: service.append_to_file(AppendToFileRequest.model_validate(data)),
        "delete_file": lambda data: service.delete_file(DeleteFileRequest.model_validate(data)),
        "create_repository_dispatch": lambda data: service.create_repository_dispatch(CreateDispatchEventRequest.model_validate(data)),
        "trigger_workflow_dispatch": lambda data: service.trigger_workflow_dispatch(TriggerWorkflowDispatchRequest.model_validate(data)),
        "list_workflow_runs": lambda data: service.list_workflow_runs(ListWorkflowRunsRequest.model_validate(data)),
    }
    if name not in handlers:
        raise KeyError(f"Unknown tool: {name}")
    result = handlers[name](arguments)
    return _tool_result(result.model_dump())


def main() -> None:
    settings = get_settings()
    logging.getLogger().setLevel(settings.log_level.upper())
    service = GitHubService(GitHubApiClient(settings))

    for raw_line in sys.stdin:
        line = raw_line.strip()
        if not line:
            continue

        request: dict[str, Any] | None = None

        try:
            parsed = json.loads(line)
            request = parsed if isinstance(parsed, dict) else None
            if request is None:
                raise ValueError("JSON-RPC request must be an object")
            request_id = request.get("id")
            method = request.get("method")

            if method == "initialize":
                response = _success_response(
                    request_id,
                    {
                        "protocolVersion": "2024-11-05",
                        "serverInfo": {
                            "name": "github-prod-mcp",
                            "version": "0.1.0",
                        },
                        "capabilities": {
                            "tools": {},
                        },
                    },
                )
            elif method == "tools/list":
                response = _success_response(request_id, {"tools": _build_tools()})
            elif method == "tools/call":
                params = request.get("params", {})
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                response = _success_response(request_id, _dispatch_tool(service, tool_name, arguments))
            elif method == "notifications/initialized":
                continue
            else:
                response = _error_response(request_id, -32601, f"Method not found: {method}")
        except GitHubApiError as exc:
            response = _error_response(request.get("id") if isinstance(request, dict) else None, -32001, exc.message, {"status_code": exc.status_code, "details": exc.details})
        except Exception as exc:
            LOGGER.exception("Unhandled MCP server error")
            response = _error_response(request.get("id") if isinstance(request, dict) else None, -32000, str(exc))

        sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()

# Made with Bob
