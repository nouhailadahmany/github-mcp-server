from __future__ import annotations

from typing import Any, Callable

from github_prod_mcp.github_api import GitHubApiClient
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
    GenericGitHubResponse,
    GetCommitRequest,
    InsertContentRequest,
    ListRepositoryFilesRequest,
    IssueIdentifierRequest,
    ListWorkflowRunsRequest,
    MergePullRequestRequest,
    OwnerRepoRequest,
    PullRequestIdentifierRequest,
    ReplaceContentRequest,
    RepositoryDetailsRequest,
    SearchCodeRequest,
    SearchIssuesRequest,
    SearchRepositoriesRequest,
    ToolCatalogResponse,
    ToolDescriptor,
    TriggerWorkflowDispatchRequest,
    UpdateIssueRequest,
)


class GitHubService:
    def __init__(self, client: GitHubApiClient) -> None:
        self._client = client

    def tool_catalog(self) -> ToolCatalogResponse:
        return ToolCatalogResponse(
            tools=[
                ToolDescriptor(name="get_authenticated_user", description="Get the authenticated GitHub user", rest_path="/tools/get_authenticated_user", request_model="None"),
                ToolDescriptor(name="create_repository", description="Create a repository for the authenticated user", rest_path="/tools/create_repository", request_model="CreateRepositoryRequest"),
                ToolDescriptor(name="get_repository", description="Get repository metadata", rest_path="/tools/get_repository", request_model="OwnerRepoRequest"),
                ToolDescriptor(name="list_branches", description="List repository branches", rest_path="/tools/list_branches", request_model="OwnerRepoRequest"),
                ToolDescriptor(name="get_branch", description="Get a branch by name", rest_path="/tools/get_branch", request_model="BranchRequest"),
                ToolDescriptor(name="get_repository_details", description="Get repository details including optional branches, root files, and README metadata", rest_path="/tools/get_repository_details", request_model="RepositoryDetailsRequest"),
                ToolDescriptor(name="list_repository_files", description="List repository files or directory contents", rest_path="/tools/list_repository_files", request_model="ListRepositoryFilesRequest"),
                ToolDescriptor(name="get_file_content", description="Get repository file content metadata", rest_path="/tools/get_file_content", request_model="FileContentRequest"),
                ToolDescriptor(name="search_repositories", description="Search repositories", rest_path="/tools/search_repositories", request_model="SearchRepositoriesRequest"),
                ToolDescriptor(name="search_code", description="Search code", rest_path="/tools/search_code", request_model="SearchCodeRequest"),
                ToolDescriptor(name="search_issues", description="Search issues and pull requests", rest_path="/tools/search_issues", request_model="SearchIssuesRequest"),
                ToolDescriptor(name="list_issues", description="List repository issues", rest_path="/tools/list_issues", request_model="OwnerRepoRequest"),
                ToolDescriptor(name="get_issue", description="Get an issue", rest_path="/tools/get_issue", request_model="IssueIdentifierRequest"),
                ToolDescriptor(name="create_issue", description="Create an issue", rest_path="/tools/create_issue", request_model="CreateIssueRequest"),
                ToolDescriptor(name="update_issue", description="Update an issue", rest_path="/tools/update_issue", request_model="UpdateIssueRequest"),
                ToolDescriptor(name="create_issue_comment", description="Create an issue comment", rest_path="/tools/create_issue_comment", request_model="CreateCommentRequest"),
                ToolDescriptor(name="list_pull_requests", description="List pull requests", rest_path="/tools/list_pull_requests", request_model="OwnerRepoRequest"),
                ToolDescriptor(name="get_pull_request", description="Get a pull request", rest_path="/tools/get_pull_request", request_model="PullRequestIdentifierRequest"),
                ToolDescriptor(name="create_pull_request", description="Create a pull request", rest_path="/tools/create_pull_request", request_model="CreatePullRequestRequest"),
                ToolDescriptor(name="merge_pull_request", description="Merge a pull request", rest_path="/tools/merge_pull_request", request_model="MergePullRequestRequest"),
                ToolDescriptor(name="get_commit", description="Get a commit", rest_path="/tools/get_commit", request_model="GetCommitRequest"),
                ToolDescriptor(name="compare_commits", description="Compare commits", rest_path="/tools/compare_commits", request_model="CompareCommitsRequest"),
                ToolDescriptor(name="create_or_update_file", description="Create or update a repository file", rest_path="/tools/create_or_update_file", request_model="CreateOrUpdateFileRequest"),
                ToolDescriptor(name="insert_content", description="Insert content at a specific line in a file without recreating it", rest_path="/tools/insert_content", request_model="InsertContentRequest"),
                ToolDescriptor(name="replace_content", description="Replace specific content in a file without recreating it", rest_path="/tools/replace_content", request_model="ReplaceContentRequest"),
                ToolDescriptor(name="append_to_file", description="Append content to an existing repository file", rest_path="/tools/append_to_file", request_model="AppendToFileRequest"),
                ToolDescriptor(name="delete_file", description="Delete a repository file", rest_path="/tools/delete_file", request_model="DeleteFileRequest"),
                ToolDescriptor(name="create_repository_dispatch", description="Create a repository dispatch event", rest_path="/tools/create_repository_dispatch", request_model="CreateDispatchEventRequest"),
                ToolDescriptor(name="trigger_workflow_dispatch", description="Trigger a workflow dispatch", rest_path="/tools/trigger_workflow_dispatch", request_model="TriggerWorkflowDispatchRequest"),
                ToolDescriptor(name="list_workflow_runs", description="List workflow runs", rest_path="/tools/list_workflow_runs", request_model="ListWorkflowRunsRequest"),
            ]
        )

    def _wrap(self, operation: str, fn: Callable[[], Any]) -> GenericGitHubResponse:
        return GenericGitHubResponse(operation=operation, data=fn())

    def get_authenticated_user(self) -> GenericGitHubResponse:
        return self._wrap("get_authenticated_user", self._client.get_authenticated_user)

    def create_repository(self, request: CreateRepositoryRequest) -> GenericGitHubResponse:
        payload = request.model_dump(exclude_none=True)
        return self._wrap("create_repository", lambda: self._client.create_repository(payload))

    def get_repository(self, request: OwnerRepoRequest) -> GenericGitHubResponse:
        return self._wrap("get_repository", lambda: self._client.get_repository(request.owner, request.repo))

    def list_branches(self, request: OwnerRepoRequest) -> GenericGitHubResponse:
        return self._wrap("list_branches", lambda: self._client.list_branches(request.owner, request.repo))

    def get_branch(self, request: BranchRequest) -> GenericGitHubResponse:
        return self._wrap("get_branch", lambda: self._client.get_branch(request.owner, request.repo, request.branch))

    def get_repository_details(self, request: RepositoryDetailsRequest) -> GenericGitHubResponse:
        def operation() -> Any:
            repository = self._client.get_repository(request.owner, request.repo)
            result: dict[str, Any] = {"repository": repository}

            if request.include_branches:
                result["branches"] = self._client.list_branches(request.owner, request.repo)

            if request.include_root_files:
                result["root_files"] = self._client.list_repository_files(request.owner, request.repo)

            if request.include_readme:
                result["readme"] = self._client.get_readme(request.owner, request.repo)

            return result

        return self._wrap("get_repository_details", operation)

    def list_repository_files(self, request: ListRepositoryFilesRequest) -> GenericGitHubResponse:
        return self._wrap(
            "list_repository_files",
            lambda: self._client.list_repository_files(request.owner, request.repo, request.path, request.ref),
        )

    def get_file_content(self, request: FileContentRequest) -> GenericGitHubResponse:
        return self._wrap(
            "get_file_content",
            lambda: self._client.get_file_content(request.owner, request.repo, request.path, request.ref),
        )

    def search_repositories(self, request: SearchRepositoriesRequest) -> GenericGitHubResponse:
        return self._wrap(
            "search_repositories",
            lambda: self._client.search_repositories(
                request.query,
                request.sort,
                request.order,
                request.per_page,
                request.page,
            ),
        )

    def search_code(self, request: SearchCodeRequest) -> GenericGitHubResponse:
        return self._wrap(
            "search_code",
            lambda: self._client.search_code(
                request.query,
                request.sort,
                request.order,
                request.per_page,
                request.page,
            ),
        )

    def search_issues(self, request: SearchIssuesRequest) -> GenericGitHubResponse:
        return self._wrap(
            "search_issues",
            lambda: self._client.search_issues(
                request.query,
                request.sort,
                request.order,
                request.per_page,
                request.page,
            ),
        )

    def list_issues(self, request: OwnerRepoRequest) -> GenericGitHubResponse:
        return self._wrap("list_issues", lambda: self._client.list_issues(request.owner, request.repo))

    def get_issue(self, request: IssueIdentifierRequest) -> GenericGitHubResponse:
        return self._wrap("get_issue", lambda: self._client.get_issue(request.owner, request.repo, request.issue_number))

    def create_issue(self, request: CreateIssueRequest) -> GenericGitHubResponse:
        return self._wrap(
            "create_issue",
            lambda: self._client.create_issue(
                request.owner,
                request.repo,
                request.title,
                request.body,
                request.assignees,
                request.labels,
                request.milestone,
            ),
        )

    def update_issue(self, request: UpdateIssueRequest) -> GenericGitHubResponse:
        payload = request.model_dump(exclude={"owner", "repo", "issue_number"}, exclude_none=True)
        return self._wrap(
            "update_issue",
            lambda: self._client.update_issue(request.owner, request.repo, request.issue_number, payload),
        )

    def create_issue_comment(self, request: CreateCommentRequest) -> GenericGitHubResponse:
        return self._wrap(
            "create_issue_comment",
            lambda: self._client.create_issue_comment(request.owner, request.repo, request.issue_number, request.body),
        )

    def list_pull_requests(self, request: OwnerRepoRequest) -> GenericGitHubResponse:
        return self._wrap("list_pull_requests", lambda: self._client.list_pull_requests(request.owner, request.repo))

    def get_pull_request(self, request: PullRequestIdentifierRequest) -> GenericGitHubResponse:
        return self._wrap(
            "get_pull_request",
            lambda: self._client.get_pull_request(request.owner, request.repo, request.pull_number),
        )

    def create_pull_request(self, request: CreatePullRequestRequest) -> GenericGitHubResponse:
        return self._wrap(
            "create_pull_request",
            lambda: self._client.create_pull_request(
                request.owner,
                request.repo,
                request.title,
                request.head,
                request.base,
                request.body,
                request.maintainer_can_modify,
                request.draft,
            ),
        )

    def merge_pull_request(self, request: MergePullRequestRequest) -> GenericGitHubResponse:
        return self._wrap(
            "merge_pull_request",
            lambda: self._client.merge_pull_request(
                request.owner,
                request.repo,
                request.pull_number,
                request.commit_title,
                request.commit_message,
                request.merge_method,
            ),
        )

    def get_commit(self, request: GetCommitRequest) -> GenericGitHubResponse:
        return self._wrap("get_commit", lambda: self._client.get_commit(request.owner, request.repo, request.ref))

    def compare_commits(self, request: CompareCommitsRequest) -> GenericGitHubResponse:
        return self._wrap(
            "compare_commits",
            lambda: self._client.compare_commits(request.owner, request.repo, request.basehead),
        )

    def create_or_update_file(self, request: CreateOrUpdateFileRequest) -> GenericGitHubResponse:
        return self._wrap(
            "create_or_update_file",
            lambda: self._client.create_or_update_file(
                request.owner,
                request.repo,
                request.path,
                request.message,
                request.content,
                request.branch,
                request.sha,
                request.committer,
                request.author,
            ),
        )

    def append_to_file(self, request: AppendToFileRequest) -> GenericGitHubResponse:
        return self._wrap(
            "append_to_file",
            lambda: self._client.append_to_file(
                request.owner,
                request.repo,
                request.path,
                request.content,
                request.message,
                request.branch,
                request.committer,
                request.author,
            ),
        )

    def delete_file(self, request: DeleteFileRequest) -> GenericGitHubResponse:
        return self._wrap(
            "delete_file",
            lambda: self._client.delete_file(
                request.owner,
                request.repo,
                request.path,
                request.message,
                request.sha,
                request.branch,
                request.committer,
                request.author,
            ),
        )

    def create_repository_dispatch(self, request: CreateDispatchEventRequest) -> GenericGitHubResponse:
        return self._wrap(
            "create_repository_dispatch",
            lambda: self._client.create_repository_dispatch(
                request.owner,
                request.repo,
                request.event_type,
                request.client_payload,
            ),
        )

    def trigger_workflow_dispatch(self, request: TriggerWorkflowDispatchRequest) -> GenericGitHubResponse:
        return self._wrap(
            "trigger_workflow_dispatch",
            lambda: self._client.trigger_workflow_dispatch(
                request.owner,
                request.repo,
                request.workflow_id,
                request.ref,
                request.inputs,
            ),
        )

    def list_workflow_runs(self, request: ListWorkflowRunsRequest) -> GenericGitHubResponse:
        return self._wrap(
            "list_workflow_runs",
            lambda: self._client.list_workflow_runs(
                request.owner,
                request.repo,
                request.actor,
                request.branch,
                request.event,
                request.status,
                request.per_page,
                request.page,
            ),
        )

    def insert_content(self, request: InsertContentRequest) -> GenericGitHubResponse:
        return self._wrap(
            "insert_content",
            lambda: self._client.insert_content(
                request.owner,
                request.repo,
                request.path,
                request.line_number,
                request.content,
                request.message,
                request.branch,
                request.committer,
                request.author,
            ),
        )

    def replace_content(self, request: ReplaceContentRequest) -> GenericGitHubResponse:
        return self._wrap(
            "replace_content",
            lambda: self._client.replace_content(
                request.owner,
                request.repo,
                request.path,
                request.old_content,
                request.new_content,
                request.message,
                request.branch,
                request.replace_all,
                request.occurrence,
                request.committer,
                request.author,
            ),
        )

# Made with Bob
