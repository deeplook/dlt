from typing import Any, Dict, Optional, Union

from dlt.sources.helpers import requests

BASE_URL = "https://cloud.getdbt.com/api"


class InvalidCredentialsException(Exception):
    pass


class DBTCloudClientV2:
    """
    A client for interacting with the dbt Cloud API (version 2).
    """

    def __init__(
        self,
        api_token: str,
        account_id: Optional[str] = None,
        base_api_url: str = BASE_URL,
    ):
        """
        Args:
            api_token (str): The API token for authentication.
            account_id (str, optional): The ID of the dbt Cloud account.
                Defaults to None.
            base_api_url (str, optional): The base URL of the dbt Cloud API.
                Defaults to "https://cloud.getdbt.com/api".
        """
        self.api_version = "v2"
        self.base_api_url = f"{base_api_url}/{self.api_version}"
        self._api_token = api_token
        self._headers = {
            "Content-Type": "application/json",
            "Authorization": f"Token {self._api_token}",
            "Accept": "application/json",
        }

        self.account_id = account_id
        self.accounts_url = f"accounts/{self.account_id}"

    def get_endpoint(self, endpoint: str) -> Any:
        response = requests.get(f"{self.base_api_url}/{endpoint}", headers=self._headers)
        results = response.json()
        return results

    def post_endpoint(self, endpoint: str, json_body: Optional[Dict[Any, Any]] = None) -> Any:
        response = requests.post(
            f"{self.base_api_url}/{endpoint}",
            headers=self._headers,
            json=json_body,
        )
        results = response.json()
        return results

    def trigger_job_run(self, job_id: Union[int, str], data: Optional[Dict[Any, Any]] = None) -> int:
        """
         Trigger a job run in dbt Cloud.

        Uses `https://cloud.getdbt.com/api/v2/accounts/{account_id}/jobs/{job_id}/run/`
        endpoint to kick off a run for a job.

        When this endpoint returns a successful response, a new run will be enqueued
        for the account. Users can poll the Get run endpoint to poll the run until it completes.
        After the run has completed, users can use the Get run artifact endpoint to download artifacts generated by the run.

        More info: https://docs.getdbt.com/dbt-cloud/api-v2#/operations/Trigger%20Job%20Run.

         Args:
             job_id (int | str): The ID of the job.

             data (dict, optional): The JSON data to post. Defaults to None.
                 Fields of data:
                 '{
                    "cause": "string",
                    "git_sha": "string",
                    "git_branch": "string",
                    "azure_pull_request_id": integer,
                    "github_pull_request_id": integer,
                    "gitlab_merge_request_id": integer,
                    "schema_override": "string",
                    "dbt_version_override": "string",
                    "threads_override": integer,
                    "target_name_override": "string",
                    "generate_docs_override": boolean,
                    "timeout_seconds_override": integer,
                    "steps_override": [
                        "string"
                    ]
                }'

         Returns:
             int: The ID of the triggered job run.

         Raises:
             InvalidCredentialsException: If account_id or job_id is missing.

        """
        if not (self.account_id and job_id):
            raise InvalidCredentialsException(f"account_id and job_id are required, got account_id: {self.account_id} and job_id: {job_id}")

        json_body = {}
        if data:
            json_body.update(data)

        response = self.post_endpoint(f"{self.accounts_url}/jobs/{job_id}/run", json_body=json_body)
        return int(response["data"]["id"])

    def get_run_status(self, run_id: Union[int, str]) -> Dict[Any, Any]:
        """
        Get the status of a dbt Cloud job run by run_id.

        Uses `https://cloud.getdbt.com/api/v2/accounts/{account_id}/runs/{id}/`
        to get job run information.

        More info: https://docs.getdbt.com/dbt-cloud/api-v2#/operations/Retrieve%20Run.

        Args:
            run_id (int | str): The ID of the job run.

        Returns:
            Dict[Any, Any]: The status information of the job run.

        Raises:
            InvalidCredentialsException: If account_id or run_id is missing.

        """
        if not (self.account_id and run_id):
            raise InvalidCredentialsException(f"account_id and run_id are required, got account_id: {self.account_id} and run_id: {run_id}.")

        response = self.get_endpoint(f"{self.accounts_url}/runs/{run_id}")
        return dict(response["data"])
