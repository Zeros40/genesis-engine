"""Workflow #1 - Lead Router.

Captures an inbound lead, qualifies it against the ideal client profile
with a Mistral model, applies deterministic routing thresholds, and
produces a personalized reply draft. The workflow returns a structured
decision; the actual sending of the email is a later iteration (needs a
workspace secret for email delivery).
"""

from pydantic import BaseModel, Field

import mistralai.workflows as workflows
from mistralai.workflows import Depends
from mistralai.workflows.client import get_mistral_client


class LeadInput(BaseModel):
    name: str
    company: str
    email: str
    message: str = ""
    source: str = "website"
    booking_link: str = "https://cal.com/zodiachub2026/intro-call"


class Qualification(BaseModel):
    score: int = Field(ge=0, le=100)
    reason: str
    draft_email: str


ICP_SYSTEM_PROMPT = """You are the lead qualification engine of an AI automation practice that serves dome, modular and prefabricated construction manufacturers.

Score the lead from 0 to 100 against this ideal client profile:
- The company is a manufacturer, builder, or supplier in dome, modular, prefab, or construction-adjacent industries (highest weight).
- The lead appears to be a decision maker (owner, director, manager) or close to one.
- The message reveals operational pain that AI can remove: repetitive quoting, design and proposal work, document handling, lead follow-up, support, reporting.
- There is a signal of budget or seriousness: asking about pricing, timelines, concrete problems, or requesting a call.

Rules:
- Clear buying intent with a fitting company: 70-100.
- Good fit but vague message: 35-69.
- Poor fit, spam, job seeker, or unrelated: 0-34.

Then write a short personalized reply draft (max 150 words) from Mohamed at the practice. It must:
- Reference something specific from the lead's message or company.
- In one sentence, name one concrete automation that would remove their repetitive quoting and admin work.
- Invite them to a 15-minute intro call and include the booking link provided in the lead details, exactly as given.
- Professional, warm, no fluff.

Respond with JSON only, exactly this shape:
{"score": <integer 0-100>, "reason": "<one sentence>", "draft_email": "<email body text>"}
"""


@workflows.activity()
async def qualify_lead(lead: dict, client=Depends(get_mistral_client)) -> dict:
    """Call the model to score the lead and draft a personalized reply."""
    user_prompt = (
        "Lead details:\n"
        f"Name: {lead['name']}\n"
        f"Company: {lead['company']}\n"
        f"Email: {lead['email']}\n"
        f"Source: {lead['source']}\n"
        f"Booking link: {lead['booking_link']}\n"
        f"Message:\n{lead['message'] or '(no message provided)'}\n\n"
        "Score this lead and write the reply draft. JSON only."
    )
    response = await client.chat.complete_async(
        model="mistral-small-latest",
        messages=[
            {"role": "system", "content": ICP_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
    )
    raw = response.choices[0].message.content
    start = raw.find("{")
    end = raw.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError(f"Model returned no parsable JSON: {raw[:200]}")
    parsed = Qualification.model_validate_json(raw[start : end + 1])
    return parsed.model_dump()


@workflows.workflow.define(
    name="lead-router",
    workflow_display_name="Lead Router",
    workflow_description="Qualifies an inbound lead with AI and returns a routing decision plus a personalized reply draft.",
)
class LeadRouterWorkflow:
    @workflows.workflow.entrypoint
    async def run(self, input: LeadInput) -> dict:
        lead = input.model_dump()
        qualification = await qualify_lead(lead)
        score = qualification["score"]

        if score >= 60:
            decision = "book_meeting"
            next_step = "Send the draft with the booking link; this lead is qualified."
        elif score >= 35:
            decision = "nurture"
            next_step = "Send the draft and add the lead to the nurture sequence."
        else:
            decision = "decline"
            next_step = "Send a polite decline; do not offer a meeting."

        return {
            "lead": lead,
            "score": score,
            "decision": decision,
            "reason": qualification["reason"],
            "draft_email": qualification["draft_email"],
            "next_step": next_step,
        }
