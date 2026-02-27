"""
Email Drafting Agent
Analyzes incoming emails and generates contextual draft responses using OpenAI's API.
"""

import os
import json
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def analyze_email(email_content: str) -> dict:
    """
    Analyze an incoming email to extract key information.

    Args:
        email_content: The raw text of the email to analyze.

    Returns:
        A dict with keys: intent, tone, key_points, urgency, action_required.
    """
    prompt = f"""Analyze the following email and return a JSON object with these fields:
- intent: the main purpose of the email (e.g. "request", "complaint", "inquiry", "follow-up")
- tone: the emotional tone (e.g. "formal", "urgent", "friendly", "frustrated")
- key_points: a list of the 3 most important points from the email
- urgency: one of "low", "medium", or "high"
- action_required: a brief description of what response or action is needed

Email:
\"\"\"
{email_content}
\"\"\"

Respond with only valid JSON, no additional text."""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are an expert email analyst. Extract structured information from emails accurately.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
        response_format={"type": "json_object"},
    )

    return json.loads(response.choices[0].message.content)


def generate_draft_response(
    email_content: str,
    analysis: dict | None = None,
    sender_name: str = "",
    your_name: str = "",
    additional_context: str = "",
) -> str:
    """
    Generate a draft response to an email.

    Args:
        email_content: The original email text.
        analysis: Optional pre-computed analysis dict from analyze_email().
        sender_name: Name of the person who sent the email.
        your_name: Your name, used to sign the draft.
        additional_context: Any extra context or instructions for shaping the reply.

    Returns:
        A string containing the drafted email response.
    """
    if analysis is None:
        analysis = analyze_email(email_content)

    context_block = f"\nAdditional context: {additional_context}" if additional_context else ""
    sender_block = f"The sender's name is {sender_name}." if sender_name else ""
    signature_block = f"Sign the email as '{your_name}'." if your_name else "Do not include a signature name."

    prompt = f"""You are drafting a professional email response.

Original email:
\"\"\"
{email_content}
\"\"\"

Email analysis:
- Intent: {analysis.get('intent', 'unknown')}
- Tone: {analysis.get('tone', 'neutral')}
- Urgency: {analysis.get('urgency', 'medium')}
- Action required: {analysis.get('action_required', '')}
- Key points: {', '.join(analysis.get('key_points', []))}
{sender_block}{context_block}

Instructions:
- Match the professionalism level of the original email.
- Address all key points and required actions.
- Be concise and clear.
- {signature_block}

Write only the email body (including greeting and sign-off), no subject line or metadata."""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are an expert email writer. Draft clear, professional, and contextually appropriate email responses.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
    )

    return response.choices[0].message.content.strip()


def process_email(
    email_content: str,
    sender_name: str = "",
    your_name: str = "",
    additional_context: str = "",
) -> dict:
    """
    Full pipeline: analyze an email and generate a draft response.

    Args:
        email_content: The raw email text.
        sender_name: Name of the sender (optional).
        your_name: Your name for the sign-off (optional).
        additional_context: Extra instructions for the reply (optional).

    Returns:
        A dict with 'analysis' and 'draft_response' keys.
    """
    print("Analyzing email...")
    analysis = analyze_email(email_content)

    print("Generating draft response...")
    draft = generate_draft_response(
        email_content,
        analysis=analysis,
        sender_name=sender_name,
        your_name=your_name,
        additional_context=additional_context,
    )

    return {"analysis": analysis, "draft_response": draft}


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

SAMPLE_EMAIL = """
Subject: Urgent: Project Deadline Extension Request

Hi,

I hope this message finds you well. I'm writing to request a two-week extension
on the Q1 analytics report that is currently due on March 15th.

Our team has encountered unexpected data quality issues with three of the primary
data sources. We discovered inconsistencies last Wednesday and have been working
around the clock to resolve them, but a thorough fix will require additional time
to ensure the report's accuracy.

We understand the impact this may have on downstream planning and we sincerely
apologize for any inconvenience. We are committed to delivering a high-quality,
accurate report and believe a revised deadline of March 29th is achievable.

Please let me know if you'd like to schedule a call to discuss this further.

Best regards,
Alex Johnson
Senior Data Analyst
"""


def main():
    if not os.environ.get("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable is not set.")
        print("Set it with: export OPENAI_API_KEY='your-api-key-here'")
        return

    print("=" * 60)
    print("EMAIL DRAFTING AGENT - DEMO")
    print("=" * 60)
    print("\nIncoming Email:")
    print("-" * 40)
    print(SAMPLE_EMAIL.strip())
    print("-" * 40)

    result = process_email(
        email_content=SAMPLE_EMAIL,
        sender_name="Alex Johnson",
        your_name="Jordan Smith",
        additional_context="Approve the extension but request a brief status update by March 22nd.",
    )

    print("\nEmail Analysis:")
    print("-" * 40)
    analysis = result["analysis"]
    print(f"  Intent   : {analysis.get('intent')}")
    print(f"  Tone     : {analysis.get('tone')}")
    print(f"  Urgency  : {analysis.get('urgency')}")
    print(f"  Action   : {analysis.get('action_required')}")
    print("  Key Points:")
    for point in analysis.get("key_points", []):
        print(f"    - {point}")

    print("\nDraft Response:")
    print("-" * 40)
    print(result["draft_response"])
    print("=" * 60)


if __name__ == "__main__":
    main()
