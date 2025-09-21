function startReview() {
  const prUrl = prompt("Enter PR URL:");
  if (!prUrl) return;

  fetch("/review", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ pr_url: prUrl })
  })
  .then(res => res.json())
  .then(data => {
    alert(`PR: ${data.pr_url}\nScore: ${data.score}\nInsight: ${data.insight}`);
  })
  .catch(err => console.error(err));
}
