import hashlib

def calculate_file_hash(content: bytes) -> str:
    """Calculate SHA256 hash of a file's content"""
    sha256 = hashlib.sha256()
    sha256.update(content)
    return sha256.hexdigest()
