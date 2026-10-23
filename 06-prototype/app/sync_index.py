"""Feed the circular library into Pinecone.

Reads library/register.csv, opens every Live circular PDF, splits it into sections (with the
page each starts on), and upserts them to Pinecone, which embeds the text itself with its
hosted multilingual-e5-large model. Superseded versions are never sent, and the namespace is
cleared first, so a replaced circular leaves the index on the next sync (guardrail G-10).

Run from the 06-prototype folder:  python app/sync_index.py
"""
import os, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kamilisha as k


def main():
    k.load_dotenv()
    if not os.environ.get("PINECONE_API_KEY"):
        sys.exit("PINECONE_API_KEY is missing from the .env file.")
    from pinecone import Pinecone
    pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
    if not pc.has_index(k.INDEX_NAME):
        print(f"Creating index {k.INDEX_NAME} (multilingual-e5-large)...")
        pc.create_index_for_model(name=k.INDEX_NAME, cloud="aws", region="us-east-1",
                                  embed={"model": "multilingual-e5-large", "field_map": {"text": "chunk_text"}})
    index = pc.Index(k.INDEX_NAME)
    try:                                   # start clean: only today's Live sections stay in the index
        index.delete(delete_all=True, namespace=k.NAMESPACE)
    except Exception:
        pass                               # namespace does not exist yet on the first run
    live = k.live_sections(k.load_library())
    records = [{"_id": s.sid, "chunk_text": k.section_text(s), "circular": s.circular,
                "version": s.version, "section": s.number} for s in live]
    batch = 90                             # Pinecone accepts at most 96 records per request
    for i in range(0, len(records), batch):
        index.upsert_records(namespace=k.NAMESPACE, records=records[i:i + batch])
        print(f"  sent {min(i + batch, len(records))}/{len(records)}")
    print(f"Loaded {len(records)} Live sections from "
          f"{len({s.circular for s in live})} circulars. Waiting for Pinecone to index them...")
    time.sleep(15)
    test = k.PineconeRetriever(index).search("Mteja amepoteza kadi", live, k=3)
    print("Check search (Swahili: 'customer lost card'):")
    for s, score in test:
        print(f"  {score:.3f}  {s.citation}  {s.heading}")


if __name__ == "__main__":
    main()
