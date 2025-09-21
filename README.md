# PR Reviewer

A web app for automated code review of pull requests using AI.  
Supports GitHub, GitLab, and Bitbucket PRs. Built with FastAPI, Jinja2, and Google Generative AI.

![PR Reviewer Screenshot](https://raw.githubusercontent.com/asterisk51/PR-review-agent/main/webapp/static/img/image.png)

## Features

- Enter a PR link or details to get an AI-powered review
- Supports multiple git providers (GitHub, GitLab, Bitbucket)
- Simple web UI
- Color-coded feedback and scores

## Quick Start

1. **Clone the repo**
   ```sh
   git clone https://github.com/yourusername/yourrepo.git
   cd yourrepo
   ```

2. **Install dependencies**
   ```sh
   pip install -r requirements.txt
   ```

3. **Set environment variables**  
   Create a `.env` file in the root:
   ```
   GITHUB_TOKEN=your_github_token
   GOOGLE_API_KEY=your_google_api_key
   ```

4. **Run the app**
   ```sh
   uvicorn webapp.app:app --reload
   ```

5. **Open in browser:**  
   [http://localhost:8000](http://localhost:8000)

## Deployment

Deploy easily to [Render](https://render.com/) or any cloud that supports Python and FastAPI.


