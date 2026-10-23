# AI factsheet: Kamilisha

A one-page summary for governance review, updated at every release.

| | |
| --- | --- |
| **Version and status** | 0.2, UAT passed (run 3, 23 October 2026); before the pilot: business sign-off and independent validation |
| **Business owner** | Head of Branch Operations (fictional) |
| **Delivery owner** | Data Management Office |
| **Purpose** | Help branch staff find and follow the current procedure ([intended use](intended-use.md)) |
| **Users** | Branch staff; training unit sees aggregated reports only |
| **Not for** | Customers; approvals or decisions; customer data |
| **Sources** | Live circulars in the Kamilisha library: pilot covers card replacement, business account opening and annual leave |
| **How it works** | Retrieval-augmented generation: a vector search (Pinecone, multilingual-e5-large, in the prototype) finds the five most relevant Live sections; the model writes short steps from those sections only; the citation is attached from the library. Tool-neutral: the search and the model are swappable parts |
| **Languages** | English source; answers in plain English or Swahili |
| **Human oversight** | Staff check cited sections before acting on control steps; owners review samples weekly; escalation by severity ([oversight](oversight-and-escalation.md)) |
| **Known limits** | Three procedures only in the pilot. Only as accurate as the library. Swahili is generated, not human-translated. Cannot judge facts about a specific customer |
| **Fairness** | Answer quality is reported separately for English and Swahili, so Swahili users get the same standard |
| **Data protection** | No customer personal data stored; masking and incident route (G-06). Designed for Tanzania's Personal Data Protection Act, 2022 |
| **Pass mark before go-live** | At least 95% correct answers with correct citations; 100% on not-found, workaround and personal-data cases ([BRD](../03-define/brd.md)) |
| **Monitoring** | Weekly: adoption, active users, answer quality, wrong or unclear rate, not-found rate ([KPIs](../04-baseline/kpi-definitions.md)) |
| **Change control** | Any model or library change reruns the full test pack before release (R10) |
| **Third-party services** | Prototype: Anthropic (answers) and Pinecone (search). Production needs IT security approval or bank-hosted equivalents (R12) |
| **Main risks** | Wrong answer, outdated source, over-trust, low adoption ([risk register](risk-register.csv)) |
