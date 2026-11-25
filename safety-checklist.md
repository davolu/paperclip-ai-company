# Safety checklist (run before you press Run now)

- [ ] Company budget set, hard stop on (Paperclip warns at 80%, pauses at 100%)
- [ ] Per-agent budgets set for every agent
- [ ] Timer heartbeats OFF (`runtimeConfig.heartbeat.enabled: false`) — wake agents with Run now
- [ ] Model pinned on every agent (never `auto`, never a blank Claude model)
- [ ] Keys stored as Paperclip secrets, not pasted into visible fields
- [ ] Workspace is a local folder with no git remote
- [ ] No connectors (deploy, email, chat, social) installed
- [ ] Telemetry off: `PAPERCLIP_TELEMETRY_DISABLED=1`
- [ ] After the demo: pause every agent
- [ ] Using free (unpriced) models? Set `unpricedUsagePolicy: "allow"` on the company and agent budget policies, or the first free run trips a hard stop at $0.00
- [ ] Set a spend limit in your model provider's own console too. Paperclip could not price the models used here, so its dollar caps never counted them
