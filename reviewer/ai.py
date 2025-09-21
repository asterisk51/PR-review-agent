import os
import re
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()

class AIReviewer:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("Please set the GOOGLE_API_KEY environment variable")
        genai.configure(api_key=api_key)

        # ✅ Use GenerativeModel directly
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    def review_diff(self, filename: str, diff: str) -> dict:
        """Send code diff to Gemini for review and return feedback + numeric score."""
        prompt = f"""
You are a senior software engineer reviewing a pull request.

File: {filename}

Diff:
{diff}

Please provide review feedback in this format:

### Review Comments
- (bullet point comments on readability, coding standards, possible bugs, improvements)

### Code Quality Score
- A single number between 0 and 10, where:
  0-3 = Poor, buggy or unreadable
  4-6 = Needs work, some issues
  7-8 = Good, mostly clean
  9-10 = Excellent, ready to merge
"""
        try:
            # ✅ Use generate_content instead of generate_text
            response = self.model.generate_content(prompt)

            # Gemini sometimes returns list of candidates; pick the text safely
            text = response.text.strip() if hasattr(response, "text") else str(response)

            # Split comments and score
            parts = text.split("### Code Quality Score")
            comments = (
                parts[0].replace("### Review Comments", "").strip()
                if len(parts) > 0
                else "No comments"
            )

            # Extract numeric score using regex
            raw_score = parts[1].strip() if len(parts) > 1 else "N/A"
            match = re.search(r"(\d+(\.\d+)?)", raw_score)
            score = float(match.group(1)) if match else "N/A"

            return {"comments": comments, "score": score}

        except Exception as e:
            return {"comments": f"AI Review failed: {e}", "score": "N/A"}
