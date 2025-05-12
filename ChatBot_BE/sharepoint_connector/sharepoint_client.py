from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.client_credential import ClientCredential
from .secrets_client import SecretsClient

class SharePointClient:
    def __init__(self, secrets_api_url):
        # Fetch secrets dynamically
        secrets_client = SecretsClient(secrets_api_url)
        secrets = secrets_client.get_secrets()

        self.site_url = secrets["site_url"]
        self.client_id = secrets["client_id"]
        self.client_secret = secrets["client_secret"]
        self.tenant_id = secrets["tenant_id"]
        self.library_name = secrets.get("library_name", "Documents")
        self.folder_path = secrets.get("folder_path", "")

        self.ctx = ClientContext(self.site_url).with_credentials(
            ClientCredential(self.client_id, self.client_secret)
        )

    def list_files(self, library_name=None, folder_path=None):
        library_name = library_name or self.library_name
        folder_path = folder_path or self.folder_path

        if folder_path:
            full_path = f"Shared Documents/{folder_path}"  # No encoding
            folder = self.ctx.web.get_folder_by_server_relative_url(full_path)
        else:
            folder = self.ctx.web.lists.get_by_title(library_name).root_folder

        files = folder.files.get().execute_query()

        file_list = []
        for file in files:
            file_info = {
                "Name": file.properties["Name"],
                "Url": file.properties["ServerRelativeUrl"]
            }
            file_list.append(file_info)

        return file_list

    def download_file(self, file_server_relative_url, local_path):
        """
        Download a file from SharePoint to local storage
        """
        response = self.ctx.web.get_file_by_server_relative_url(file_server_relative_url).download(local_path).execute_query()
        return response
