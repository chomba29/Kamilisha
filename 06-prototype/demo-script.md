# Demo script

Five scenarios, about five minutes. Each shows a requirement working; scenario 5 shows Kamilisha correctly saying it does not know. Use the example buttons at the top of the screen.

| # | Button | Question | What to point out | Requirements |
| --- | --- | --- | --- | --- |
| 1 | Card replacement | Customer lost their card, what do I do? | Short numbered steps; the signed blocking form comes before blocking; CONTROL badges with the circular's exact wording; "Changed on 1 Sep 2026"; source under the answer. Open "Sections retrieved" to show the blocking form added by control completion | BR-01, BR-02, BR-09, BR-10, G-13 |
| 2 | Old habit | Can I block the card on the system without the form? | Gives the current rule from version 2, not the old habit from version 1 | BR-04 |
| 3 | Swahili | Mteja amepoteza kadi, nifanye nini? | Same steps in Swahili, same source; open "Sections retrieved" to show Pinecone found the English section from a Swahili question | BR-03 |
| 4 | Business account | What documents for a business account? | Asks which type of business first; then type "Sole proprietor" to get the checklist without a business licence | BR-11, BR-01 |
| 5 | Not in library | How do I deposit a foreign currency cheque? | Says "Not found in the current circulars. Ask your supervisor." instead of guessing | BR-05 |

## If there is time

| Button | What to point out | Requirements |
| --- | --- | --- |
| Workaround | Declines, restates the blocking-form rule, logs the question for the procedure owner | BR-06 |
| Customer data | Warns and removes the account number before the question is processed or logged | BR-07 |
| (sidebar) Pause Card replacement | Switch-off: card questions now get "not found" and staff fall back to the intranet | G-11 |
| Question log tab | Questions by procedure and branch, never by staff name | BR-08, BR-13, G-12 |
| Wrong or unclear | Sends the question and answer to the procedure owner's queue | BR-12 |

## Closing line

"Pinecone finds the five most relevant current sections, in English or Swahili. Claude answers only from those. Every citation, version, page number and control wording on the screen comes from the library itself, not from the AI. If the AI cites anything it was not given, Kamilisha withholds the answer."
