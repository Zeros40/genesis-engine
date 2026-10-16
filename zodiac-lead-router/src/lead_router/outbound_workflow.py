"""Module 2 - Outbound Sequencer.

Generates a personalized 3-step cold outreach sequence for each target
company in the dome / modular / prefab construction space. Feeds the
AI Operations Sprint offer.
"""

from pydantic import BaseModel

import mistralai.workflows as workflows
from mistralai.workflows import Depends
from mistralai.workflows.client import get_mistral_client


class Target(BaseModel):
    company: str
    website: str = ""
    focus: str = ""
    contact_name: str = ""


class OutboundInput(BaseModel):
    targets: list[Target]
    sender_name: str = "Mohamed"
    booking_link: str = "https://cal.com/BOOKING-LINK"


class Sequence(BaseModel):
    company: str = ""
    subject: str
    step1: str
    step2: str
    step3: str


OUTBOUND_SYSTEM_PROMPT = """You write cold outreach for an AI automation practice serving dome, modular and prefabricated construction manufacturers.

Rules:
- step1: under 90 words. Open with a specific observation about the company's product or market. One sentence on the automation opportunity (repetitive quoting, proposals, admin, follow-up). Soft close: ask if it is worth a look.
- step2: a short bump, under 50 words, references step1, adds one concrete number such as hours per week saved.
- step3: a polite last touch, under 45 words, includes the booking link.
- Professional, warm, zero fluff, no emojis, no fake familiarity.
- Each step is plain email body text (no "Subject:" prefix).

Respond with JSON only, exactly this shape:
{"subject": "<email subject>", "step1": "<body>", "step2": "<body>", "step3": "<body>"}
"""


@workflows.activity()
async def generate_sequence(target: dict, sender_name: str, booking_link: str, client=Depends(get_mistral_client)) -> dict:
    """Generate a personalized 3-step outreach sequence for one target."""
    user_prompt = (
        f"Target company: {target['company']}\n"
        f"Website: {target['website'] or '(not provided)'}\n"
        f"Focus / products: {target['focus'] or '(infer from the company name)'}\n"
        f"Contact name: {target['contact_name'] or '(unknown, use a generic greeting)'}\n"
        f"Sender: {sender_name}\n"
        f"Booking link: {booking_link}\n\n"
        "Write the 3-step sequence. JSON only."
    )
    response = await client.chat.complete_async(
        model="mistral-small-latest",
        messages=[
            {"role": "system", "content": OUTBOUND_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
    )
    raw = response.choices[0].message.content
    start = raw.find("{")
    end = raw.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError(f"Model returned no parsable JSON: {raw[:200]}")
    parsed = Sequence.model_validate_json(raw[start : end + 1])
    out = parsed.model_dump()
    out["company"] = target["company"]
    return out


@workflows.workflow.define(
    name="outbound-sequencer",
    workflow_display_name="Outbound Sequencer",
    workflow_description="Generates a personalized 3-step cold outreach sequence for each target company.",
)
class OutboundSequencerWorkflow:
    @workflows.workflow.entrypoint
    async def run(self, input: OutboundInput) -> dict:
        sequences = []
        for target in input.targets:
            sequences.append(
                await generate_sequence(target.model_dump(), input.sender_name, input.booking_link)
            )
        return {"count": len(sequences), "sequences": sequences}
