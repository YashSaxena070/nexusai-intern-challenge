Q1: Our STT sends partial transcripts every 200ms while the customer is still speaking. Should we start querying the database on partial results or wait until they finish? Describe your approach and the specific tradeoffs. 

-> If the speech-to-text system sends partial transcripts every 200 ms, I would not immediately start full database queries for each partial update. That would generate a huge number of unnecessary requests because the sentence may change as the user continues speaking. Instead, I would use a hybrid approach. I would monitor the partial transcripts to detect early intent signals, but delay any expensive operations until the system is reasonably confident the user has finished or the intent is clear.

For example, if the partial transcript already includes a strong signal like “cancel my service,” we could start lightweight preparation steps in the background (like loading the customer account or ticket history). However, full database queries or workflow decisions should wait until the final transcript arrives. This reduces wasted compute and prevents incorrect assumptions caused by incomplete sentences.

The tradeoff is between speed and accuracy. Acting on partial transcripts can reduce response time, but it also increases the chance of doing unnecessary work or misclassifying the request. Waiting for the final transcript improves reliability but adds a slight delay. The balanced approach is to do lightweight prefetching during speech and commit to real actions only after the final transcript is received.


Q2: Our system auto-adds any resolution with CSAT ≥ 4 to the knowledge base. Describe two specific ways this could go wrong over 6 months and how you would prevent each one.

-> Automatically adding solutions with CSAT scores of 4 or higher to the knowledge base sounds useful, but over time it could create some problems. One issue is that incorrect or temporary fixes might enter the knowledge base. For example, a customer might give a high CSAT because the agent was polite, even though the actual solution was not technically correct or only worked in that specific situation. After six months, the knowledge base could contain misleading information that the AI starts repeating to other customers.

To prevent this, I would introduce a review layer before adding new entries. For example, resolutions could first be stored in a “candidate knowledge” pool. Only solutions that appear multiple times with good CSAT scores would be promoted into the official knowledge base. This ensures the information is reliable and not based on a single case.

Another problem is knowledge duplication or clutter. Many slightly different versions of the same solution could accumulate over time, making the knowledge base harder to maintain. To prevent this, I would periodically run similarity checks to merge duplicate entries and organize them by intent. Regular review and deduplication would keep the knowledge base clean and useful over the long term.


Q3: A customer says "I've been without internet for 4 days, I called 3 times already, your company is useless and I want to cancel right now." What does the AI do, step by step? What does it say? What does it pass to the human agent?

-> In this situation the system should recognize several warning signals immediately. The customer mentions being without internet for four days, having called three times already, and expresses strong frustration. The sentiment score would likely be very negative and the intent “service cancellation” is also present. Based on the escalation rules, the AI should quickly decide that this case needs human intervention rather than trying to fully resolve it automatically.

The AI should first respond in a calm and empathetic way to acknowledge the frustration. For example, it might say something like: “I’m really sorry you’ve had to deal with this for several days. I can see how frustrating that must be.” It should then inform the customer that it will connect them to a human specialist who can handle the issue more directly.

At the same time, the system prepares a context summary for the human agent. This summary would include the customer’s account information, previous tickets, how long the outage has lasted, the negative sentiment detected, and the customer’s request to cancel service. Passing this context ensures the human agent does not need to ask the customer to repeat everything, which helps reduce frustration and speeds up the resolution process.


Q4: What is the single most important thing you would add to improve this system? Not "more training data." Pick one specific feature or change, explain how you'd build it, and say how you'd measure whether it worked. 

-> One improvement I would add to the system is a customer frustration tracking mechanism that works across multiple interactions. Currently, the system looks at a single conversation to determine sentiment or escalation, but it would be much more helpful to track a rolling frustration score for each customer over time. For example, if a customer has contacted support three times in a short period and each conversation shows negative sentiment, the system should treat that situation differently from a normal support request.

To build this, I would store sentiment scores and escalation events for each interaction in the database. A small service could calculate a “frustration index” based on recent history, such as the last 7 or 14 days. If the index crosses a threshold, the system could automatically prioritize the case, escalate faster, or route the customer directly to a specialized support team.

To measure whether this improvement works, I would track metrics like repeat complaint rates, escalation resolution time, and CSAT scores for high-frustration customers. If those metrics improve after introducing the frustration index, it would show that the system is handling difficult situations more effectively.


