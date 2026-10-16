"""Worker entrypoint for the Zodiac backbone deployment."""

import asyncio

import mistralai.workflows as workflows

from lead_router.lead_workflow import LeadRouterWorkflow
from lead_router.outbound_workflow import OutboundSequencerWorkflow
from lead_router.nurture_workflow import LeadNurtureWorkflow


async def main() -> None:
    await workflows.run_worker(
        [LeadRouterWorkflow, OutboundSequencerWorkflow, LeadNurtureWorkflow]
    )


if __name__ == "__main__":
    asyncio.run(main())
