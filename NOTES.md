# Test Cases and Results

## Test 1: Billing, high confidence

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



## Test 2: Account access

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



## Test 3: Vague problem, human fallback

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



## Test 4: Technical issue

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



## Test 5: General enquiry

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

## Debug note

Early test run showed the raw parsed response before routing logic was confirmed:

```
CATEGORY: billing
CONFIDENCE: 95
REASON: The client explicitly states they were charged twice on their credit card, which is a clear billing issue.

lines: ['CATEGORY: billing', 'CONFIDENCE: 95', 'REASON: The client explicitly states they were charged twice on their credit card, which is a clear billing issue.']
```

The `lines` print statement was used for debugging and can be removed.