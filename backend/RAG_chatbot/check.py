# fix_test_data.py
import chromadb

print("Fixing test data...")

client = chromadb.PersistentClient(path='./chroma_db')
collection = client.get_or_create_collection('rag_documents')

# Delete old test data
print("Deleting old test data...")
try:
    collection.delete(ids=['test_1', 'test_2', 'test_3'])
    print("✅ Deleted")
except:
    print("⚠️ No test data to delete")

# Add new data with user_id
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')

texts = ["East: 2500", "West: 1800", "Central: 2200"]
embeddings = model.encode(texts).tolist()

collection.add(
    ids=['test_1', 'test_2', 'test_3'],
    embeddings=embeddings,
    documents=texts,
    metadatas=[
        {'region': 'East', 'user_id': 8},      # ✅ Added user_id
        {'region': 'West', 'user_id': 8},      # ✅ Added user_id
        {'region': 'Central', 'user_id': 8}    # ✅ Added user_id
    ]
)

print("✅ Added test data with user_id=8")
print(f"✅ Total documents: {collection.count()}")

# Verify
all_data = collection.get()
print("\n📊 Metadata:")
for meta in all_data['metadatas']:
    print(f"  {meta}")
