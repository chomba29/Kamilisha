# User stories and acceptance criteria

Circular IDs refer to the fictional demo library defined in [data-requirements.md](data-requirements.md).

## Cards

**US-01 Card replacement steps.** As a customer service officer, I want the card replacement steps in order, so that I don't miss a control.
- **Given** CIR-CARD-07 v2 is Live
- **When** I ask "Customer lost their card, what do I do?"
- **Then** I get numbered steps, with "Obtain signed card-blocking form" before "Block old card", both marked CONTROL, and the citation CIR-CARD-07 v2, section and page *(BR-01, BR-02, BR-09)*

**US-02 Current version only.** As a customer service officer, I want the current rule, not the old habit.
- **Given** CIR-CARD-07 v1 is Superseded and v2 is Live
- **When** I ask "Can I block the card without the form?"
- **Then** the answer says the signed form is required first, cites v2 only, and shows "changed on 1 Sep 2026" *(BR-04, BR-10)*

**US-03 Swahili.** As a teller, I want to ask in Swahili.
- **Given** CIR-CARD-07 v2 is Live
- **When** I ask "Mteja amepoteza kadi, nifanye nini?"
- **Then** I get the same steps in Swahili with the same citation *(BR-03)*

## Business account opening

**US-04 Documents checklist.** As a relationship officer, I want the documents list for a sole proprietor, so that the customer makes one trip.
- **Given** CIR-ACC-12 v2 is Live
- **When** I ask "What documents does a sole proprietor need?"
- **Then** I get a checklist that accepts a tax registration certificate in place of a business licence, marked CONTROL, citing CIR-ACC-12 v2 and showing "changed on 15 Aug 2026" *(BR-01, BR-02, BR-09, BR-10)*

**US-05 Missing facts.** As a relationship officer, I want to be asked for the entity type rather than given a wrong list.
- **Given** the documents list differs by entity type
- **When** I ask "What documents for a business account?"
- **Then** I am asked to choose sole proprietor, partnership or company before any list is shown *(BR-11)*

## Staff affairs

**US-06 Leave notice.** As a staff member, I want to know how much notice annual leave needs.
- **Given** HR-POL-03 v2 is Live
- **When** I ask "How early must I apply for annual leave?"
- **Then** the answer gives the v2 notice period with its citation, and no "changed on" flag because the change is older than 90 days *(BR-01, BR-02, BR-04, BR-10)*

## Safety and feedback (all procedures)

**US-07 Not found.** As any staff member, I want an honest "not found" rather than a guess.
- **Given** no Live circular covers foreign-currency cheque deposits
- **When** I ask about them
- **Then** the reply is exactly "Not found in the current circulars. Ask your supervisor." and the log records Not found *(BR-05, BR-08)*

**US-08 Control bypass.** As the Cards procedure owner, I want workaround questions declined and reported.
- **Given** the blocking form is a control
- **When** someone asks "Can I block now and get the form signed tomorrow?"
- **Then** the request is declined, the control is restated with its citation, and the question is logged as Declined for the procedure owner *(BR-06, BR-08)*

**US-09 Personal data.** As Compliance, I want customer data kept out.
- **Given** a staff member types a customer name and account number
- **When** the question is submitted
- **Then** the answer reminds them not to enter customer data, and the log stores the question with the name and number masked *(BR-07)*

**US-10 Wrong or unclear.** As a procedure owner, I want to hear when an answer is wrong or unclear.
- **Given** an answer is shown
- **When** the staff member presses "Wrong or unclear"
- **Then** the question, answer and citation reach the procedure owner's queue *(BR-12)*

**US-11 Training dashboard.** As a training officer, I want to see what staff ask most.
- **Given** a week of logged questions
- **When** I open the dashboard
- **Then** I see the top questions by procedure and branch, with not-found and declined counts *(BR-13)*
