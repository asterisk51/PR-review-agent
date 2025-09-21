import argparse
import os
from dotenv import load_dotenv
from reviewer.git_clients import GitHubClient
from reviewer.ai import AIReviewer

def main():
    load_dotenv()

    parser = argparse.ArgumentParser(description="PR Review Agent (CLI)")
    parser.add_argument("--repo", required=True, help="Repo in format owner/repo")
    parser.add_argument("--pr", required=True, type=int, help="Pull request number")
    args = parser.parse_args()

    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print(" Error: Please set GITHUB_TOKEN in .env")
        return

    client = GitHubClient(token)
    reviewer = AIReviewer()

    files = client.get_pr_files(args.repo, args.pr)

    print(f"🔹 Found {len(files)} changed file(s) in PR #{args.pr}\n")
    for f in files:
        filename = f['filename']
        diff = f.get('patch')
        if not diff:
            continue

        print(f" {filename} ({f['status']})")
        print("---- AI Review ----")
        result = reviewer.review_diff(filename, diff[:1000])
        print(result["comments"])
        print(f"\n Code Quality Score: {result['score']}")
        print("\n============================\n")

if __name__ == "__main__":
    main()
