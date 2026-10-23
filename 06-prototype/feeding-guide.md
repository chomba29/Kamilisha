# Feeding the library into Pinecone: step by step

This guide loads the 12 Live circulars (209 sections) into Pinecone and checks the result. It takes about 15 minutes the first time. Commands are for Anaconda Prompt on Windows, run from the `06-prototype` folder.

## What happens when you "feed" Pinecone

1. **Read the register:** `library/register.csv` says which version of each circular is Live.
2. **Open the Live PDFs:** the 12 current circulars. The 3 Superseded ones are never sent.
3. **Split into sections:** each numbered section, appendix and FAQ answer becomes one record, with its circular, version and page number. That gives 209 records.
4. **Send to Pinecone:** Pinecone turns each record's text into a vector (a list of numbers that captures its meaning) with its hosted multilingual-e5-large model, and stores it.
5. **Search:** when staff ask a question, Pinecone turns the question into a vector the same way and returns the 5 closest sections, in English or Swahili.

## Step 1: Get a Pinecone API key

1. Sign up for a free account at pinecone.io.
2. In the Pinecone console, open **API keys** and create a key.
3. Copy the key. Keep it private: anyone with it can use your account.

## Step 2: Open the project folder

Open **Anaconda Prompt** and run:

```
cd C:\Users\User\Desktop\my_comliance_buddy_2026\github_ready\06-prototype
```

## Step 3: Install the tools

```
pip install -r requirements.txt
```

## Step 4: Add your keys

```
copy .env.example .env
notepad .env
```

Paste your keys after `ANTHROPIC_API_KEY=` and `PINECONE_API_KEY=`, with no spaces or quotes. Save and close. The `.env` file stays on your computer; `.gitignore` keeps it off GitHub.

## Step 5: Look at what you are about to feed (optional)

Open `library\pdf\CIR-CARD-07-v2.pdf` to see a circular, and `library\register.csv` to see the register.

## Step 6: Feed Pinecone

```
python app\sync_index.py
```

You should see:

```
Creating index kamilisha-circulars (multilingual-e5-large)...
  sent 90/209
  sent 180/209
  sent 209/209
Loaded 209 Live sections from 12 circulars. Waiting for Pinecone to index them...
Check search (Swahili: 'customer lost card'):
  0.8xx  CIR-CARD-07 v2, section 5.x, page x  ...
```

The first line only appears the first time, when the index is created. The scores in the last lines will differ; what matters is that card replacement sections come back for a Swahili question.

## Step 7: Check it in the Pinecone console

Open **Indexes**, then **kamilisha-circulars**. The namespace `live` should hold 209 records. You can open a record to see its text, circular, version and section.

## Step 8: Measure retrieval

```
python app\eval_retrieval.py
```

This runs 21 questions (13 English, 8 Swahili) through both searches and reports three things per language: whether the answer is in the top 5, whether the control step is in the top 5, and whether the control step reaches Claude after control completion. Results are saved in `logs\retrieval_eval.csv`, which is replaced on each run.

## Step 9: Use it in the app

```
streamlit run app\app.py
```

The sidebar should say **Search: Pinecone semantic search (multilingual-e5-large)**. Ask a question and open **Sections retrieved** to see what Pinecone found.

## When a circular changes

1. Edit its file in `library\source\` (or add a new version and mark the old one Superseded).
2. Rebuild the PDFs: `python library\build_library.py`
3. Feed Pinecone again: `python app\sync_index.py`. Old sections are cleared first, so a replaced version cannot come back.

## If something goes wrong

| Message | What to do |
| --- | --- |
| `PINECONE_API_KEY is missing from the .env file.` | Check Step 4: the key must be on the `PINECONE_API_KEY=` line and the file saved as `.env`, not `.env.txt` |
| `Unauthorized` or `401` | The key is wrong or was deleted; create a new one in the console |
| An error that mentions the region or your plan | Your Pinecone plan may not allow the region `us-east-1`; check the regions your plan offers and change `region=` in `app\sync_index.py` |
| The app sidebar says "keyword search" | The app could not reach Pinecone; check the key and your internet connection, then restart the app |
| A Swahili question finds nothing useful | Rerun Step 6, then Step 8, and send the results for review |
