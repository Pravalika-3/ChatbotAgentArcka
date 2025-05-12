import json
import os

METADATA_FILE = "resume_metadata.json"

class ResumeMetadataManager:
    def __init__(self, metadata_file: str = METADATA_FILE):
        self.metadata_file = metadata_file
        self.metadata = self.load_metadata()

    def load_metadata(self):
        """Load existing metadata or initialize new"""
        if os.path.exists(self.metadata_file):
            with open(self.metadata_file, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            return {}

    def save_metadata(self):
        """Save metadata to file"""
        with open(self.metadata_file, "w", encoding="utf-8") as f:
            json.dump(self.metadata, f, indent=2)

    def check_if_update_needed(self, filename, last_modified, file_hash):
        """Check if the file needs to be downloaded/updated"""
        entry = self.metadata.get(filename)
        if not entry:
            return True  # New file
        if entry["last_modified"] != last_modified or entry["file_hash"] != file_hash:
            return True  # Updated file
        return False  # No change

    def update_metadata(self, filename, last_modified, file_size, file_hash, candidate_name):
        """Update or insert metadata entry"""
        self.metadata[filename] = {
            "last_modified": last_modified,
            "file_size": file_size,
            "file_hash": file_hash,
            "candidate_name": candidate_name
        }
        self.save_metadata()
