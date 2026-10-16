"""Worker entrypoint for the Zodiac lead router deployment."""

import asyncio

import mistralai.workflows as workflows

from lead_router.lead_workflow import LeadRouterWorkflow


async def main() -> None:
    await workflows.run_worker([LeadRouterWorkflow])


if __name__ == "__main__":
    asyncio.run(main())
