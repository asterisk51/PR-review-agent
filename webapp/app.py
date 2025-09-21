import sys
import os
import asyncio
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from reviewer.git_clients import GitHubClient, GitLabClient, BitbucketClient
from reviewer.ai import AIReviewer

ai_reviewer = AIReviewer()

from dotenv import load_dotenv  # to load .env files

# --- Load environment variables ---
load_dotenv()  # ensure your .env is loaded
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
# GITLAB_TOKEN = os.getenv("GITLAB_TOKEN")
# BITBUCKET_USER = os.getenv("BITBUCKET_USER")
# BITBUCKET_APP_PASS = os.getenv("BITBUCKET_APP_PASS")

if not GITHUB_TOKEN:
    raise RuntimeError("GITHUB_TOKEN environment variable is missing!")
# if not GITLAB_TOKEN:
#     raise RuntimeError("GITLAB_TOKEN environment variable is missing!")
# if not BITBUCKET_USER or not BITBUCKET_APP_PASS:
#     raise RuntimeError("Bitbucket credentials are missing!")

# --- FastAPI setup ---
app = FastAPI()
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")
templates = Jinja2Templates(directory="templates")

# --- Initialize clients ---
clients = {
    "github": GitHubClient(token=GITHUB_TOKEN),
    # "gitlab": GitLabClient(token=GITLAB_TOKEN),
    # "bitbucket": BitbucketClient(username=BITBUCKET_USER, app_password=BITBUCKET_APP_PASS)
}

# --- Helpers ---
def score_color(score):
    try:
        score = float(score)
    except (ValueError, TypeError):
        return "gray"  

    if score >= 8:
        return "green"
    elif score >= 6:
        return "yellow"
    else:
        return "red"


async def analyze_pr(files):
    """Analyze PR files using AIReviewer."""
    results = []

    for f in files:
        fname = f.get("filename") or f.get("new_path") or f.get("path")
        diff = f.get("patch", "")

        # Skip files with no diff
        if not diff:
            results.append({
                "filename": fname,
                "status": "No changes",
                "score": "N/A",
                "comments": "No diff available"
            })
            continue

        # Run AI review
        review = ai_reviewer.review_diff(fname, diff)

        # Determine status based on score
        score = review.get("score")
        status = "Approved" if isinstance(score, (int, float)) and score >= 7 else "Changes Requested"

        results.append({
            "filename": fname,
            "status": status,
            "score": score,
            "comments": review.get("comments", "No comments")
        })

    return results

# --- Routes ---
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "feedback_results": [],
        "error": None,
        "score_color": score_color
    })

@app.post("/", response_class=HTMLResponse)
async def review_pr(
    request: Request,
    provider: str = Form(None),
    repo: str = Form(None),
    pr: int = Form(None)
):
    if not provider or not repo or pr is None:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "feedback_results": [],
            "error": "All fields (provider, repo, pr) are required.",
            "score_color": score_color
        })

    provider_lower = provider.lower()
    client = clients.get(provider_lower)

    if client is None:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "feedback_results": [],
            "error": f"Invalid provider selected: {provider}",
            "score_color": score_color
        })

    try:
        files = client.get_pr_files(repo, pr)
        feedback_results = await analyze_pr(files)
        error = None
    except Exception as e:
        feedback_results = []
        error = str(e)

    return templates.TemplateResponse("index.html", {
        "request": request,
        "feedback_results": feedback_results,
        "error": error,
        "score_color": score_color
    })
