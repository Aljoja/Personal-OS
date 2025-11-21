from brain.memory import Memory

memory = Memory()

print("="*60)
print("Checking Saved Conversations")
print("="*60)

# Get ALL conversations
try:
    all_convs = memory.conversations.get()
    
    print(f"\nTotal conversations saved: {len(all_convs['ids'])}")
    
    if all_convs['ids']:
        print("\nAll conversations:")
        for i, (conv_id, doc, meta) in enumerate(zip(
            all_convs['ids'][:10],  # Show first 10
            all_convs['documents'][:10],
            all_convs['metadatas'][:10]
        ), 1):
            timestamp = meta.get('timestamp', 'Unknown')[:19]
            preview = doc[:100].replace('\n', ' ')
            print(f"\n{i}. [{timestamp}]")
            print(f"   ID: {conv_id}")
            print(f"   Preview: {preview}...")
    else:
        print("\nNo conversations found!")
        
except Exception as e:
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)