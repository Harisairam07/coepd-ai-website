"""Test chatbot intent detection and responses for all query types."""
import sys
sys.path.insert(0, ".")

from chatbot.intent_engine import detect_intent
from chatbot.chatbot_engine import FAQ_ANSWERS, COURSE_DETAILS_ACTIONS, get_bot_response
from chatbot.faq import knowledge_base

print("=" * 60)
print("INTENT DETECTION TESTS")
print("=" * 60)

test_cases = [
    # Fees
    ("What are the course fees?", "fees"),
    ("How much does BA training cost?", "fees"),
    ("What is the pricing?", "fees"),
    ("program cost", "fees"),
    # Internship
    ("Do you provide internship?", "internship"),
    ("intern opportunities", "internship"),
    # Placement support
    ("Which program includes placement support?", "placement_support"),
    ("placement program details", "placement_support"),
    # Placement general
    ("Tell me about placement", "placement"),
    # Course details
    ("course details", "course_details"),
    ("Tell me the syllabus", "course_details"),
    ("what will i learn", "course_details"),
    ("program information", "course_details"),
    ("course structure", "course_details"),
    ("training program", "course_details"),
    ("ba training details", "course_details"),
    ("program details", "course_details"),
    # Duration
    ("How long is the course?", "duration"),
    # Batch
    ("weekend batch", "batch_timings"),
]

all_pass = True
for query, expected in test_cases:
    result = detect_intent(query)
    ok = result == expected
    if not ok:
        all_pass = False
    print(f"  {'PASS' if ok else 'FAIL'}: '{query}' => {result} (expected {expected})")

print("\n" + "=" * 60)
print("COURSE DETAILS RESPONSE CONTENT")
print("=" * 60)
cd = FAQ_ANSWERS["course_details"]
checks = [
    ("Has 6 Months BA Program", "6 Months Business Analyst Training Program" in cd),
    ("Has Theory + Practical", "2 Hours Theory" in cd),
    ("Has Balsamiq", "Balsamiq" in cd),
    ("Has Jira", "Jira" in cd),
    ("Has Tableau", "Tableau" in cd),
    ("Has SQL", "SQL" in cd),
    ("Has Power BI", "Power BI" in cd),
    ("Has Draw.io", "Draw.io" in cd),
    ("Has Agile & Scrum", "Agile & Scrum" in cd),
    ("Has 3 Capstone Projects", "3 Capstone Projects" in cd),
    ("Has 2 Real-Time Live Projects", "2 Real-Time Live Projects" in cd),
]
for label, result in checks:
    if not result:
        all_pass = False
    print(f"  {'PASS' if result else 'FAIL'}: {label}")

print("\n" + "=" * 60)
print("COURSE DETAILS QUICK ACTIONS")
print("=" * 60)
expected_labels = {"Program Benefits", "Placement Support", "Batch Timings", "Book Free Demo"}
actual_labels = {a["label"] for a in COURSE_DETAILS_ACTIONS}
match = expected_labels == actual_labels
if not match:
    all_pass = False
print(f"  {'PASS' if match else 'FAIL'}: Quick actions = {actual_labels}")

print("\n" + "=" * 60)
print("CHATBOT ENGINE INTEGRATION")
print("=" * 60)
resp = get_bot_response("Tell me the course details", "test_user_cd")
resp_text = resp.get("text", "")
resp_opts = [o["label"] for o in resp.get("options", [])]
has_content = "6 Months Business Analyst Training Program" in resp_text
has_btns = "Program Benefits" in resp_opts and "Book Free Demo" in resp_opts
no_duplicate_demo = "Would you like to book a free demo session?" not in resp_text
if not has_content:
    all_pass = False
if not has_btns:
    all_pass = False
if not no_duplicate_demo:
    all_pass = False
print(f"  {'PASS' if has_content else 'FAIL'}: Response contains full course details")
print(f"  {'PASS' if has_btns else 'FAIL'}: Shows correct quick action buttons: {resp_opts}")
print(f"  {'PASS' if no_duplicate_demo else 'FAIL'}: No duplicate 'book a free demo' appended")

print("\n" + "=" * 60)
print("KNOWLEDGE BASE CHECK")
print("=" * 60)
kb = knowledge_base["course_structure"]
kb_ok = "6 Months Business Analyst Training Program" in kb and "Jira" in kb and "3 Capstone Projects" in kb
if not kb_ok:
    all_pass = False
print(f"  {'PASS' if kb_ok else 'FAIL'}: knowledge_base['course_structure'] has correct content")

print("\n" + "=" * 60)
print(f"RESULT: {'ALL TESTS PASSED' if all_pass else 'SOME TESTS FAILED'}")
print("=" * 60)
