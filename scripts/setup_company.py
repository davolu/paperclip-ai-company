"""Configure Harbor Bean Co. in a local Paperclip (local_trusted mode, loopback only).

Reads GEMINI_API_KEY / ANTHROPIC_API_KEY from the environment and stores them as
Paperclip secrets. Never prints key values. Writes ids to state.json.
"""
import json, os, sys, urllib.request, urllib.error, pathlib

API = os.environ.get("PAPERCLIP_API", "http://127.0.0.1:3100/api")
HERE = pathlib.Path(__file__).resolve().parent.parent
STATE = pathlib.Path(os.environ.get("STATE_FILE", HERE / "scripts" / "state.json"))
WORKSPACE = os.environ["HARBOR_WORKSPACE"]

def call(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(API + path, data=data, method=method,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            txt = r.read().decode()
            return json.loads(txt) if txt else {}
    except urllib.error.HTTPError as e:
        print(method, path, "->", e.code, e.read().decode()[:600]); raise

state = json.loads(STATE.read_text()) if STATE.exists() else {}
cid = state.get("companyId") or next(c["id"] for c in call("GET", "/companies") if c["name"] == "Harbor Bean Co.")
state["companyId"] = cid

# Company budget: $5.00 safety ceiling (not a forecast).
call("PATCH", f"/companies/{cid}/budgets", {"budgetMonthlyCents": int(os.environ.get("COMPANY_CAP_CENTS", 500))})

# Secrets (values never printed)
existing = {s["name"]: s["id"] for s in call("GET", f"/companies/{cid}/secrets")}
def secret(name, envvar):
    if name in existing: return existing[name]
    if not os.environ.get(envvar): sys.exit(f"{envvar} not set")
    s = call("POST", f"/companies/{cid}/secrets", {"name": name, "value": os.environ[envvar], "description": f"from {envvar}"})
    return s["id"]
gem = secret("gemini-api-key", "GEMINI_API_KEY")
ant = secret("anthropic-api-key", "ANTHROPIC_API_KEY")
ref = lambda sid: {"type": "secret_ref", "secretId": sid, "version": "latest"}

goal_text = (HERE / "goal.md").read_text().split("\n", 2)[2].strip()
if "goalId" not in state:
    g = call("POST", f"/companies/{cid}/goals", {"title": "Ship the Harbor Bean Co. landing page (local only)",
             "description": goal_text, "level": "company", "status": "active"})
    state["goalId"] = g["id"]
if "projectId" not in state:
    p = call("POST", f"/companies/{cid}/projects", {"name": "Landing page", "description": "Local landing page for Harbor Bean Co. No deploys.",
             "status": "in_progress", "goalIds": [state["goalId"]],
             "workspace": {"name": "harbor-bean-workspace", "sourceType": "local_path", "cwd": WORKSPACE}})
    state["projectId"] = p["id"]

def brief(n): return (HERE / "agents" / f"{n}.md").read_text()
hb = {"heartbeat": {"enabled": False, "wakeOnDemand": True}}
# What ran in the video (2026-11-25):
#  - CEO: Claude Haiku 5.5 via the Paperclip Runner (Claude Code harness). Pin the model:
#    a blank model resolves to the far pricier Opus.
#  - Writer + Developer: free Gemini models through the Gemini CLI engine.
#    The free tier is ~5 requests/min and ~20/day per model; when the Developer's daily quota ran out
#    mid-review we switched it to Haiku. Set DEV_ON_ANTHROPIC=1 to start it there.
#  - GEMINI_CLI_TRUST_WORKSPACE=true is required, or the CLI refuses to run in the workspace.
runner = lambda model: dict(adapterType="paperclip_runner", adapterConfig={
    "model": model, "provider": "acpx", "acpxAgent": "claude", "acpxPermissionMode": "approve-all",
    "env": {"ANTHROPIC_API_KEY": ref(ant)}, "timeoutSec": 900})
gemini = lambda model: dict(adapterType="gemini_local", adapterConfig={
    "model": model, "engine": "cli", "yolo": True, "timeoutSec": 900,
    "env": {"GEMINI_API_KEY": ref(gem), "GEMINI_CLI_TRUST_WORKSPACE": {"type": "plain", "value": "true"}}})
haiku = os.environ.get("ANTHROPIC_MODEL", "claude-haiku-5-5")
agents = {
  "ceo": dict(name="CEO", role="ceo", title="CEO", reportsTo=None, capabilities="Plans strategy, writes tickets, delegates, reviews.",
              **runner(haiku), budget=100, files=brief("ceo")),
  "writer": dict(name="Writer", role="general", title="Writer", capabilities="Writes short, friendly landing-page copy.",
              **gemini(os.environ.get("WRITER_MODEL", "gemini-3.5-flash-lite")), budget=100, files=brief("writer")),
  "developer": dict(name="Developer", role="engineer", title="Developer", capabilities="Builds a local HTML/CSS landing page.",
              **(runner(haiku) if os.environ.get("DEV_ON_ANTHROPIC") else gemini(os.environ.get("DEV_MODEL", "gemini-3-flash-preview"))),
              budget=300, files=brief("developer")),
}
state.setdefault("agents", {})
for key, a in agents.items():
    if key in state["agents"]: continue
    body = {k: v for k, v in a.items() if k not in ("budget", "files")}
    if key != "ceo": body["reportsTo"] = state["agents"]["ceo"]
    body["runtimeConfig"] = hb
    body["budgetMonthlyCents"] = a["budget"]
    body["instructionsBundle"] = {"files": {"AGENTS.md": a["files"]}}
    r = call("POST", f"/companies/{cid}/agents", body)
    state["agents"][key] = r["id"]
    print("created", key, r["id"], r.get("adapterType"), (r.get("adapterConfig") or {}).get("model"), r.get("lifecycleState"), r.get("configurationWarnings"))

# Budgets default to unpricedUsagePolicy "block": free Gemini usage has no price, so the very first
# free run trips a hard stop at $0.00. "allow" lets unpriced usage through; the dollar caps still apply.
def policy(scope_type, scope_id, cents):
    call("POST", f"/companies/{cid}/budgets/policies", {"scopeType": scope_type, "scopeId": scope_id,
         "metric": "billed_cents", "windowKind": "calendar_month_utc", "amount": cents,
         "hardStopEnabled": True, "warnPercent": 80, "unpricedUsagePolicy": "allow"})
policy("company", cid, int(os.environ.get("COMPANY_CAP_CENTS", 500)))
for key, a in agents.items():
    policy("agent", state["agents"][key], a["budget"])

STATE.write_text(json.dumps(state, indent=2))
print(json.dumps({k: v for k, v in state.items()}, indent=1))
