import chromadb

# Initialize ChromaDB client (adjust the path if needed)
client = chromadb.PersistentClient(path="./chroma")  # Check your app’s config for the path
collection_name = "resumes"  # Adjust based on your app’s collection name
try:
    collection = client.get_collection(name=collection_name)
    count = collection.count()
    print(f"Total embeddings in collection '{collection_name}': {count}")
    if count > 0:
        results = collection.peek(limit=5)
        print("Sample embeddings found:", results['ids'])
    else:
        print("No embeddings found in the collection.")
except Exception as e:
    print(f"Error accessing collection: {e}")