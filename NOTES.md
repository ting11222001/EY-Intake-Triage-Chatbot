# Notes

## Scripts

`main.py`: terminal version, to test quickly locally

`api.py`: FastAPI version, the one that gets deployed

To run the terminal version:
```
python main.py
```

To run the API version:
```
uvicorn api:app --reload
```

Then, go to this API doc:
```
http://localhost:8000/docs
```





## Test Cases and Results for `main.py`

### Test 1: Billing, high confidence

**Input**
```
Name     → Priya Sharma
Problem  → Our client received an invoice for Phase 2 but we have not signed off on that milestone yet
Urgent?  → high
```

**Expected:** routes to billing, confidence above 70

**Output**
```
Bot: You will be routed to our billing team.
```



### Test 2: Account access

**Input**
```
Name     → David Chen
Problem  → Our client cannot log into the EY client portal to view their deliverables
Urgent?  → medium
```

**Expected:** routes to account access

**Output**
```
Bot: You will be routed to our account access team.
```



### Test 3: Vague problem, human fallback

**Input**
```
Name     → Tom Walsh
Problem  → The partner wants something done about the report but I am not sure what exactly
Urgent?  → low
```

**Expected:** confidence below 70, human agent message appears

**Output**
```
Bot: I'm not confident enough to classify route you automatically.
Bot: A human agent will review your case and contact you shortly.
```



### Test 4: Technical issue

**Input**
```
Name     → Maria Costa
Problem  → The PowerPoint live link stopped working during our client workshop this morning
Urgent?  → high
```

**Expected:** routes to technical support

**Output**
```
Bot: You will be routed to our technical support team.
```



### Test 5: General enquiry

**Input**
```
Name     → James Okafor
Problem  → We want to understand what AI tools EY can offer for our supply chain project
Urgent?  → medium
```

**Expected:** routes to general enquiry

**Output**
```
Bot: You will be routed to our general enquiry team.
```





## Debug Note

Early test run showed the raw parsed response before routing logic was confirmed:

```
CATEGORY: billing
CONFIDENCE: 95
REASON: The client explicitly states they were charged twice on their credit card, which is a clear billing issue.

lines: ['CATEGORY: billing', 'CONFIDENCE: 95', 'REASON: The client explicitly states they were charged twice on their credit card, which is a clear billing issue.']
```

The `lines` print statement was used for debugging and can be removed.

The response from:
```python
response = client.messages.create(
    model="claude-haiku-4-5",       # simple classification, so we can use a smaller model
    max_tokens=200,                  # stop after 200 tokens at most
    messages=[{"role": "user", "content": prompt}]
)
```

looked like this:
```
Message(id='msg_01WSBbX73t5KqtyhCjcdvM2e', container=None, content=[TextBlock(citations=None, text='CATEGORY: account access\nCONFIDENCE: 95\nREASON: The client explicitly states they cannot log in to their account, which is a clear account access issue.', type='text')], model='claude-haiku-4-5-20251001', role='assistant', stop_details=None, stop_reason='end_turn', stop_sequence=None, type='message', usage=Usage(cache_creation=CacheCreation(ephemeral_1h_input_tokens=0, ephemeral_5m_input_tokens=0), cache_creation_input_tokens=0, cache_read_input_tokens=0, inference_geo='not_available', input_tokens=181, output_tokens=38, server_tool_use=None, service_tier='standard'))
```

And `result = response.content[0].text` looked like this:
```
Bot (internal): CATEGORY: account access
CONFIDENCE: 95
REASON: The client explicitly states they cannot log into their account, which is a clear account access issue.
```





## Billing

Anthropic API needs a separate credit balance. Once topped up, create a new API key to make sure the API key and the billing balance are in sync.

Check the credit balance here: https://platform.claude.com/settings/billing





## Test Cases and Results for `api.py`

For the `/classify` endpoint in the docs UI, put these in the request body.

To run:
```
uvicorn api:app --reload
```

FastAPI gives you a free test page here: http://127.0.0.1:8000/docs

See the two endpoints, `GET /questions` and `POST /classify`. Click on `/classify`, then "Try it out", and paste the input as the request body.



### Test 1: Billing, high confidence

**Input**
```json
{
  "answers": ["Priya Sharma", "Our client received an invoice for Phase 2 but we have not signed off on that milestone yet", "high"]
}
```

**Result**
```json
{
  "category": "billing",
  "confidence": 95,
  "reason": "The client is disputing an invoice for a milestone that hasn't been completed or approved, which is clearly a billing issue.",
  "routed_to": "billing team"
}
```



### Test 2: Account access

**Input**
```json
{
  "answers": ["David Chen", "Our client cannot log into the EY client portal to view their deliverables", "medium"]
}
```

**Result**
```json
{
  "category": "account access",
  "confidence": 95,
  "reason": "The client explicitly states they cannot log into the EY client portal, which is a clear account access issue.",
  "routed_to": "account access team"
}
```



### Test 3: Vague problem, human fallback

**Input**
```json
{
  "answers": ["Tom Walsh", "The partner wants something done about the report but I am not sure what exactly", "low"]
}
```

**Result**
```json
{
  "category": "general enquiry",
  "confidence": 45,
  "reason": "The client is unclear about the specific problem, making it difficult to classify, but it appears to be a general enquiry rather than a technical, billing, or account access issue.",
  "routed_to": "human review"
}
```



### Test 4: Technical issue

**Input**
```json
{
  "answers": ["Maria Costa", "The PowerPoint live link stopped working during our client workshop this morning", "high"]
}
```

**Result**
```json
{
  "category": "technical support",
  "confidence": 95,
  "reason": "Maria is reporting a non-functional PowerPoint live link feature that failed during a client meeting, which is clearly a technical issue requiring immediate resolution.",
  "routed_to": "technical support team"
}
```



### Test 5: General enquiry

**Input**
```json
{
  "answers": ["James Okafor", "We want to understand what AI tools EY can offer for our supply chain project", "medium"]
}
```

**Result**
```json
{
  "category": "general enquiry",
  "confidence": 92,
  "reason": "The client is asking for information about AI tools and services available for a supply chain project, which is a general product inquiry rather than a specific technical, billing, or account issue.",
  "routed_to": "general enquiry team"
}
```



### Quick Test

Paste this into the `/classify` request body:
```json
{
  "answers": ["Li Ting", "I cannot log into my account", "high"]
}
```

Terminal will print:
```
Received answers:  ['Li Ting', 'I cannot log into my account', 'high']

Result:  ['CATEGORY: account access', 'CONFIDENCE: 95', 'REASON: The client explicitly states they cannot log into their account, which is a clear account access issue.']
```

Response:
```json
{
  "category": "account access",
  "confidence": 95,
  "reason": "The client explicitly states they cannot log into their account, which is a clear account access issue.",
  "routed_to": "account access team"
}
```