git clone https://github.com/himanshu748/silentshift.git silentshift-current-main
cd silentshift-current-main
colima ssh --profile silentshift -- test -d "$PWD"
python3 - <<'PYCONFIG'
import os
from pathlib import Path
import secrets

values = {
    "IRIS_IMAGE": "silentshift-iris:2026.3.0AI.154.0",
    "SILENTSHIFT_IRIS_USERNAME": "ss-judge-reviewer",
    "SILENTSHIFT_VIEWER_USERNAME": "ss-judge-viewer",
    "SILENTSHIFT_IRIS_PASSWORD": secrets.token_urlsafe(24),
    "SILENTSHIFT_VIEWER_PASSWORD": secrets.token_urlsafe(24),
    "SILENTSHIFT_GATEWAY_PASSWORD": secrets.token_urlsafe(24),
    "SILENTSHIFT_PROVIDER_MODE": "live",
    "SILENTSHIFT_AGENT_WAIT_SECONDS": "120",
    "SILENTSHIFT_EMBED_BASE_URL": "http://host.lima.internal:11434/v1/",
}
lines = Path(".env.example").read_text().splitlines()
content = "\n".join(
    line.split("=", 1)[0] + "=" + values[line.split("=", 1)[0]]
    if "=" in line and line.split("=", 1)[0] in values else line
    for line in lines
) + "\n"
with os.fdopen(os.open(".env", os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "w") as out:
    out.write(content)
print("Created private local-model configuration; no provider keys.")
PYCONFIG
uv run python scripts/fetch_ipm.py --output .local/ipm/vendor/zpm-0.10.10.xml
chmod 644 .local/ipm/vendor/zpm-0.10.10.xml
uv run python scripts/verify_bonus_release.py --source load \
  --execution-mode live --allow-model-calls --container silentshift-bonus-load-main-nov8 \
  --api-port 52913 --execute
