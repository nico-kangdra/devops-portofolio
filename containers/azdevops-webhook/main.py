from fastapi import FastAPI, Request
import os, json, subprocess, signal
from dotenv import load_dotenv

signal.signal(signal.SIGCHLD, signal.SIG_IGN)

app = FastAPI()

@app.post("/hook")
async def ado_webhook(request: Request):
    payload = await request.json()
    status = payload.get("resource", {}).get("status")

    if status != "completed":
        return {"status": "Failed", "Reason": "Status not completed"}

    pr_id = payload.get("resource", {}).get("pullRequestId")
    target_branch = payload.get("resource", {}).get("targetRefName")

    if target_branch == "refs/heads/develop":
        work_status = "Ready for Staging"
    elif target_branch == "refs/heads/staging":
        work_status = "Ready for Acceptance"
    elif target_branch == "refs/heads/main":
        work_status = "Done"
    else:
        return {"status": "Failed", "Reason": "Branch not valid"}
    
    print(f"Current Status: {status}")
    cmd = [
        "az", "repos", "pr", "work-item", "list",
        "--id", str(pr_id),
        "--output", "json"
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    work_items = json.loads(result.stdout)

    for wi in work_items:
        update_cmd = ["az", "boards", "work-item", "update", "--id", str(wi['id']), "--state", work_status]
        subprocess.run(update_cmd, capture_output=True, text=True)
        print(f"{wi['id']} updated successfully")
    return {"status": "Succeed"}

if __name__ == "__main__":
    load_dotenv()

    subprocess.run(
    ["az", "devops", "login", "--organization", f"https://dev.azure.com/{os.getenv('ADO_ORG')}"],
    input=os.getenv("AZURE_DEVOPS_PAT"),
    text=True,
    check=True
    )

    subprocess.run(
    ["az", "devops", "configure", "--defaults", f"organization=https://dev.azure.com/{os.getenv('ADO_ORG')}", f"project={os.getenv('ADO_PROJECT')}"],
    text=True,
    check=True
    )

    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 3000))
    )