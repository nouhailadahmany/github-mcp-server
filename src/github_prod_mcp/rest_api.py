from __future__ import annotations

import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

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
    InsertContentRequest,
    IssueIdentifierRequest,
    ListRepositoryFilesRequest,
    ListWorkflowRunsRequest,
    MergePullRequestRequest,
    OwnerRepoRequest,
    PullRequestIdentifierRequest,
    ReplaceContentRequest,
    RepositoryDetailsRequest,
    SearchCodeRequest,
    SearchIssuesRequest,
    SearchRepositoriesRequest,
    TriggerWorkflowDispatchRequest,
    UpdateIssueRequest,
)
from github_prod_mcp.service import GitHubService


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings = get_settings()
    service = GitHubService(GitHubApiClient(settings))
    app.state.service = service
    yield


app = FastAPI(
    title="GitHub Prod MCP REST API",
    version="0.1.0",
    lifespan=lifespan,
)


@app.exception_handler(GitHubApiError)
async def github_api_error_handler(_: Request, exc: GitHubApiError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "ok": False,
            "error": exc.message,
            "details": exc.details,
        },
    )


@app.get("/health")
async def health() -> dict[str, object]:
    return {"ok": True, "service": "github-prod-mcp-rest", "version": "0.1.0"}


@app.get("/tools")
async def list_tools() -> dict[str, object]:
    service: GitHubService = app.state.service
    return service.tool_catalog().model_dump()


@app.post("/tools/get_authenticated_user")
async def get_authenticated_user() -> dict[str, object]:
    service: GitHubService = app.state.service
    return service.get_authenticated_user().model_dump()


@app.post("/tools/create_repository")
async def create_repository(request: CreateRepositoryRequest) -> dict[str, object]:
    service: GitHubService = app.state.service
    return service.create_repository(request).model_dump()


@app.post("/tools/get_repository")
async def get_repository(request: OwnerRepoRequest) -> dict[str, object]:
    service: GitHubService = app.state.service
    return service.get_repository(request).model_dump()


@app.post("/tools/list_branches")
async def list_branches(request: OwnerRepoRequest) -> dict[str, object]:
    service: GitHubService = app.state.service
    return service.list_branches(request).model_dump()


@app.post("/tools/get_branch")
async def get_branch(request: BranchRequest) -> dict[str, object]:
    service: GitHubService = app.state.service
    return service.get_branch(request).model_dump()


@app.post("/tools/get_repository_details")
async def get_repository_details(request: RepositoryDetailsRequest) -> dict[str, object]:
    service: GitHubService = app.state.service
    return service.get_repository_details(request).model_dump()


@app.post("/tools/list_repository_files")
async def list_repository_files(request: ListRepositoryFilesRequest) -> dict[str, object]:
    service: GitHubService = app.state.service
    return service.list_repository_files(request).model_dump()


@app.post("/tools/get_file_content")
async def get_file_content(request: FileContentRequest) -> dict[str, object]:
    service: GitHubService = app.state.service
    return service.get_file_content(request).model_dump()


@app.post("/tools/search_repositories")
async def search_repositories(request: SearchRepositoriesRequest) -> dict[str, object]:
    service: GitHubService = app.state.service
    return service.search_repositories(request).model_dump()


@app.post("/tools/search_code")
async def search_code(request: SearchCodeRequest) -> dict[str, object]:
    service: GitHubService = app.state.service
    return service.search_code(request).model_dump()


@app.post("/tools/search_issues")
async def search_issues(request: SearchIssuesRequest) -> dict[str, object]:
    service: GitHubService = app.state.service
    return service.search_issues(request).model_dump()


@app.post("/tools/list_issues")
async def list_issues(request: OwnerRepoRequest) -> dict[str, object]:
    service: GitHubService = app.state.service
    return service.list_issues(request).model_dump()


@app.post("/tools/get_issue")
async def get_issue(request: IssueIdentifierRequest) -> dict[str, object]:
    service: GitHubService = app.state.service
    return service.get_issue(request).model_dump()


@app.post("/tools/create_issue")
async def create_issue(request: CreateIssueRequest) -> dict[str, object]:
    service: GitHubService = app.state.service
    return service.create_issue(request).model_dump()


@app.post("/tools/update_issue")
async def update_issue(request: UpdateIssueRequest) -> dict[str, object]:
    service: GitHubService = app.state.service
    return service.update_issue(request).model_dump()


@app.post("/tools/create_issue_comment")
async def create_issue_comment(request: CreateCommentRequest) -> dict[str, object]:
    service: GitHubService = app.state.service
    return service.create_issue_comment(request).model_dump()


@app.post("/tools/list_pull_requests")
async def list_pull_requests(request: OwnerRepoRequest) -> dict[str, object]:
    service: GitHubService = app.state.service
    return service.list_pull_requests(request).model_dump()


@app.post("/tools/get_pull_request")
async def get_pull_request(request: PullRequestIdentifierRequest) -> dict[str, object]:
    service: GitHubService = app.state.service
    return service.get_pull_request(request).model_dump()


@app.post("/tools/create_pull_request")
async def create_pull_request(request: CreatePullRequestRequest) -> dict[str, object]:
    service: GitHubService = app.state.service
    return service.create_pull_request(request).model_dump()


@app.post("/tools/merge_pull_request")
async def merge_pull_request(request: MergePullRequestRequest) -> dict[str, object]:
    service: GitHubService = app.state.service
    return service.merge_pull_request(request).model_dump()


@app.post("/tools/get_commit")
async def get_commit(request: GetCommitRequest) -> dict[str, object]:
    service: GitHubService = app.state.service
    return service.get_commit(request).model_dump()


@app.post("/tools/compare_commits")
async def compare_commits(request: CompareCommitsRequest) -> dict[str, object]:
    service: GitHubService = app.state.service
    return service.compare_commits(request).model_dump()


@app.post("/tools/create_or_update_file")
async def create_or_update_file(request: CreateOrUpdateFileRequest) -> dict[str, object]:
    service: GitHubService = app.state.service
    return service.create_or_update_file(request).model_dump()


@app.post("/tools/insert_content")
async def insert_content(request: InsertContentRequest) -> dict[str, object]:
    service: GitHubService = app.state.service
    return service.insert_content(request).model_dump()


@app.post("/tools/replace_content")
async def replace_content(request: ReplaceContentRequest) -> dict[str, object]:
    service: GitHubService = app.state.service
    return service.replace_content(request).model_dump()


@app.post("/tools/append_to_file")
async def append_to_file(request: AppendToFileRequest) -> dict[str, object]:
    service: GitHubService = app.state.service
    return service.append_to_file(request).model_dump()


@app.post("/tools/delete_file")
async def delete_file(request: DeleteFileRequest) -> dict[str, object]:
    service: GitHubService = app.state.service
    return service.delete_file(request).model_dump()


@app.post("/tools/create_repository_dispatch")
async def create_repository_dispatch(request: CreateDispatchEventRequest) -> dict[str, object]:
    service: GitHubService = app.state.service
    return service.create_repository_dispatch(request).model_dump()


@app.post("/tools/trigger_workflow_dispatch")
async def trigger_workflow_dispatch(request: TriggerWorkflowDispatchRequest) -> dict[str, object]:
    service: GitHubService = app.state.service
    return service.trigger_workflow_dispatch(request).model_dump()


@app.post("/tools/list_workflow_runs")
async def list_workflow_runs(request: ListWorkflowRunsRequest) -> dict[str, object]:
    service: GitHubService = app.state.service
    return service.list_workflow_runs(request).model_dump()


def main() -> None:
    settings = get_settings()
    port = int(os.environ.get("PORT", settings.rest_port))
    uvicorn.run(
        "github_prod_mcp.rest_api:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    main()