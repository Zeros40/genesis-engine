"""Module 3 - Nurture Sequencer.

Takes a qualified-but-not-booked inbound lead and generates a 3-touch
follow-up sequence (day 2 / day 5 / day 9) that builds value before the
gentle close.
"""

from pydantic import BaseModel

import mistralai.workflows as workflows
from mistralai.workflows import Depends
from mistralai.workflows.client import get_mistral_client


class NurtureInput(BaseModel):
    lead_name: str
    company: str
    original_message: str
    pain_point: str = ""
    sender_name: str = "Mohamed"
    booking_link: str = "https://cal.com/zodiachub2026/intro-call"


class NurturePlan(BaseModel):
    touch1_day2: str
    touch2_day5: str
    touch3_day9: str


NURTURE_SYSTEM_PROMPT = """You write follow-up emails for an AI automation practice serving dome, modular and prefabricated construction manufacturers. The lead showed interest but has not booked a call.

Rules:
- touch1 (day 2): under 80 words. Thank them, add one concrete extra insight about their stated pain. No pitch repetition.
- touch2 (day 5): under 70 words. One short case-style proof point (a manufacturer cutting quote preparation time by most of a workday each week). Ask one easy question to invite a reply.
- touch3 (day 9): under 50 words. Warm last touch, booking link, no pressure.
- Plain email body text, professional, warm, no emojis.

Respond with JSON only, exactly this shape:
{"touch1_day2": "<body>", "touch2_day5": "<body>", "touch3_day9": "<body>"}
"""


@workflows.activity()
async def generate_nurture(lead: dict, sender_name: str, booking_link: str, client=Depends(get_mistral_client)) -> dict:
    """Generate the 3-touch nurture sequence for one inbound lead."""
    user_prompt = (
        f"Lead name: {lead['lead_name']}\n"
        f"Company: {lead['company']}\n"
        f"Original message: {lead['original_message']}\n"
        f"Stated pain point: {lead['pain_point'] or '(infer from the message)'}\n"
        f"Sender: {sender_name}\n"
        f"Booking link: {booking_link}\n\n"
        "Write the 3-touch nurture sequence. JSON only."
    )
    response = await client.chat.complete_async(
        model="mistral-small-latest",
        messages=[
            {"role": "system", "content": NURTURE_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
    )
    raw = response.choices[0].message.content
    start = raw.find("{")
    end = raw.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError(f"Model returned no parsable JSON: {raw[:200]}")
    return NurturePlan.model_validate_json(raw[start : end + 1]).model_dump()


@workflows.workflow.define(
    name="lead-nurture",
    workflow_display_name="Lead Nurture",
    workflow_description="Generates a 3-touch follow-up sequence for an inbound lead that has not booked a meeting.",
)
class LeadNurtureWorkflow:
    @workflows.workflow.entrypoint
    async def run(self, input: NurtureInput) -> dict:
        sequence = await generate_nurture(
            input.model_dump(), input.sender_name, input.booking_link
        )
        return {
            "lead": {"name": input.lead_name, "company": input.company},
            "schedule": {"touch1": "day 2", "touch2": "day 5", "touch3": "day 9"},
            "emails": sequence,
        }
