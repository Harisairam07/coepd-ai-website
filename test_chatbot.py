"""Test chatbot intent detection and responses for fee/pricing/placement/internship queries."""
import sys
sys.path.insert(0, ".")

from chatbot.intent_engine import detect_intent
from chatbot.chatbot_engine import FAQ_ANSWERS
from chatbot.faq import knowledge_base

print("=" * 60)
print("INTENT DETECTION TESTS")
print("=" * 60)

test_cases = [
    ("What are the course fees?", "fees"),
    ("How much does BA training cost?", "fees"),
    ("What is the pricing?", "fees"),
    ("program cost", "fees"),
    ("Do you provide internship?", "internship"),
    ("intern opportunities", "internship"),
    ("Which program includes placement support?", "placement_support"),
    ("placement program details", "placement_support"),
    ("Tell me about placement", "placement"),
    ("course details", "course_details"),
    ("How long is the course?", "duration"),
]

all_pass = True
for query, expected in test_cases:
    result = detect_intent(query)
    ok = result == expected
    if not ok:
        all_pass = False
    print(f"  {'PASS' if ok else 'FAIL'}: '{query}' => {result} (expected {expected})")

print("\n" + "=" * 60)
print("FAQ_ANSWERS KEY CHECK")
print("=" * 60)
required_keys = ["fees", "placement_support", "internship", "placement", "course_details", "duration", "batch_timings"]
for key in required_keys:
    exists = key in FAQ_ANSWERS
    if not exists:
        all_pass = False
    print(f"  {'PASS' if exists else 'FAIL'}: FAQ_ANSWERS['{key}'] exists")

print("\n" + "=" * 60)
print("KNOWLEDGE_BASE KEY CHECK")
print("=" * 60)
kb_keys = ["fees", "placement_programs", "internship_programs"]
for key in kb_keys:
    exists = key in knowledge_base
    if not exists:
        all_pass = False
    print(f"  {'PASS' if exists else 'FAIL'}: knowledge_base['{key}'] exists")

print("\n" + "=" * 60)
print("CONTENT SPOT CHECKS")
print("=" * 60)
checks = [
    ("fees response has 1,00,000", "1,00,000" in FAQ_ANSWERS["fees"]),
    ("fees response has 1,18,000", "1,18,000" in FAQ_ANSWERS["fees"]),
    ("fees response has Placement Guarantee", "Placement Guarantee" in FAQ_ANSWERS["fees"]),
    ("fees response has Refund", "40,000" in FAQ_ANSWERS["fees"]),
    ("placement_support has Placement Guarantee", "Placement Guarantee" in FAQ_ANSWERS["placement_support"]),
    ("placement_support has 3\u20135 interviews", "3\u20135 interviews" in FAQ_ANSWERS["placement_support"]),
    ("internship has 6-Month", "6-Month" in FAQ_ANSWERS["internship"]),
    ("internship has Placement Guarantee", "Placement Guarantee" in FAQ_ANSWERS["internship"]),
    ("kb fees has 1,18,000", "1,18,000" in knowledge_base["fees"]),
]
for label, result in checks:
    if not result:
        all_pass = False
    print(f"  {'PASS' if result else 'FAIL'}: {label}")

print("\n" + "=" * 60)
print(f"RESULT: {'ALL TESTS PASSED' if all_pass else 'SOME TESTS FAILED'}")
print("=" * 60)
