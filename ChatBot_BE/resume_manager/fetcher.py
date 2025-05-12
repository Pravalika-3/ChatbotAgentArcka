import os
import requests
from resume_manager.utils import calculate_file_hash
from resume_manager.metadata_manager import ResumeMetadataManager

class SharePointFetcher:
    def __init__(self, access_token, site_id, folder_path, download_dir="resumes"):
        self.access_token = access_token
        self.site_id = site_id
        self.folder_path = folder_path
        self.download_dir = download_dir
        self.base_url = "https://graph.microsoft.com/v1.0"
        self.metadata_manager = ResumeMetadataManager()

        os.makedirs(self.download_dir, exist_ok=True)

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json"
        }

    def fetch_and_update(self):
        """Main method to fetch files from SharePoint and download new/updated ones"""
        url = f"{self.base_url}/sites/{self.site_id}/drive/root:/{self.folder_path}:/children"
        response = requests.get(url, headers=self._headers())
        response.raise_for_status()
        files = response.json().get("value", [])

        print(f"Found {len(files)} files in SharePoint folder.")
        
        for file in files:
            filename = file["name"]
            last_modified = file["lastModifiedDateTime"]
            file_url = file["@microsoft.graph.downloadUrl"]

            print(f"Checking file: {filename}")
            file_content = self._download_file(file_url)
            file_hash = calculate_file_hash(file_content)

            if self.metadata_manager.check_if_update_needed(filename, last_modified, file_hash):
                print(f"Downloading updated file: {filename}")
                self._save_file(filename, file_content)
                
                candidate_name = self._extract_candidate_name(filename)
                file_size = len(file_content)

                self.metadata_manager.update_metadata(
                    filename, last_modified, file_size, file_hash, candidate_name
                )
            else:
                print(f"No update needed for {filename}.")

    def _download_file(self, download_url):
        """Download file content"""
        response = requests.get(download_url)
        response.raise_for_status()
        return response.content

    def _save_file(self, filename, content):
        """Save file to local directory"""
        filepath = os.path.join(self.download_dir, filename)
        with open(filepath, "wb") as f:
            f.write(content)

    def _extract_candidate_name(self, filename):
        """Basic logic to extract candidate name (can be improved later)"""
        name_part = filename.split("{")[0] if "{" in filename else filename
        name_part = os.path.splitext(name_part)[0]
        return name_part.strip()
