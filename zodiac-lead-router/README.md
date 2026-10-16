# zodiac-lead-router (Workflow #1)

AI lead qualification and routing for the Zodiac Domes automation backbone.
Lives on the zodiac-backbone branch of genesis-engine; main is untouched.

- Workflow name: lead-router
- Input: {"name", "company", "email", "message", "source"}
- Output: score, decision, reason, draft email, next step

No secrets are stored here: the managed deployment injects a rotating
service-account token into the worker at runtime.
