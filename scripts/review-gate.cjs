var __defProp = Object.defineProperty;
var __getOwnPropDesc = Object.getOwnPropertyDescriptor;
var __getOwnPropNames = Object.getOwnPropertyNames;
var __hasOwnProp = Object.prototype.hasOwnProperty;
var __export = (target, all) => {
  for (var name in all)
    __defProp(target, name, { get: all[name], enumerable: true });
};
var __copyProps = (to, from, except, desc) => {
  if (from && typeof from === "object" || typeof from === "function") {
    for (let key of __getOwnPropNames(from))
      if (!__hasOwnProp.call(to, key) && key !== except)
        __defProp(to, key, { get: () => from[key], enumerable: !(desc = __getOwnPropDesc(from, key)) || desc.enumerable });
  }
  return to;
};
var __toCommonJS = (mod) => __copyProps(__defProp({}, "__esModule", { value: true }), mod);

// scripts/review-gate.ts
var review_gate_exports = {};
__export(review_gate_exports, {
  STATUS_CONTEXT: () => STATUS_CONTEXT,
  evaluateReview: () => evaluateReview,
  refreshPull: () => refreshPull
});
module.exports = __toCommonJS(review_gate_exports);
var STATUS_CONTEXT = "review-complete";
var CODEX_BOT = "chatgpt-codex-connector[bot]";
var SUMMARY_MARKER = "<!-- codex-pull-request-review-summary -->";
function evaluateReview(head, comments) {
  const summary = comments.filter((c) => c.user?.login === CODEX_BOT && c.user.type === "Bot" && c.body?.includes(SUMMARY_MARKER)).sort((a, b) => b.updated_at.localeCompare(a.updated_at) || b.id - a.id)[0];
  if (!summary) return { state: "pending", description: "Waiting for Codex review on the latest commit" };
  const match = summary.body.match(/<!-- codex-review-state:v1 (\{[^\n]*\}) -->/);
  if (!match) return { state: "failure", description: "Unknown Codex summary format; review gate needs attention" };
  let data;
  try {
    data = JSON.parse(match[1]);
  } catch {
    return { state: "failure", description: "Invalid Codex summary; review gate needs attention" };
  }
  if (!data || typeof data !== "object") return { state: "failure", description: "Invalid Codex review state" };
  const review = data.code_review;
  if (!review || review.commit_sha !== head) return { state: "pending", description: "Latest commit has not been reviewed by Codex" };
  const request = comments.filter((c) => ["OWNER", "MEMBER", "COLLABORATOR"].includes(c.author_association || "") && /(?:^|\s)@codex[ \t]+(?:security[ \t]+)?review\b/i.test(c.body || "")).sort((a, b) => b.updated_at.localeCompare(a.updated_at) || b.id - a.id)[0];
  if (request && request.updated_at >= summary.updated_at) return { state: "pending", description: "Waiting for Codex to finish the new review request" };
  if (review.status !== "completed") {
    return {
      state: ["failed", "error", "cancelled"].includes(review.status || "") ? "failure" : "pending",
      description: "Codex code review is not completed"
    };
  }
  const security = data.security_review;
  if (security?.status && (security.commit_sha !== head || security.status !== "completed")) {
    return { state: "pending", description: "Waiting for the requested Codex security review" };
  }
  return { state: "success", description: "Latest commit reviewed; all review threads must also be resolved" };
}
async function refreshPull(github, repo, number) {
  const { data: pull } = await github.rest.pulls.get({ ...repo, pull_number: number });
  if (pull.state !== "open" || !["dev", "main"].includes(pull.base.ref)) return null;
  const target_url = `https://github.com/${repo.owner}/${repo.repo}/pull/${number}`;
  const post = (status2) => github.rest.repos.createCommitStatus({
    ...repo,
    sha: pull.head.sha,
    context: STATUS_CONTEXT,
    target_url,
    ...status2
  });
  await post({ state: "pending", description: "Checking latest Codex review state" });
  const comments = await github.paginate(
    "GET /repos/{owner}/{repo}/issues/{issue_number}/comments",
    { ...repo, issue_number: number, per_page: 100 }
  );
  const status = evaluateReview(pull.head.sha, comments);
  const current = await github.rest.pulls.get({ ...repo, pull_number: number });
  if (current.data.head.sha !== pull.head.sha || current.data.state !== "open") return null;
  await post(status);
  return status;
}
// Annotate the CommonJS export names for ESM import in node:
0 && (module.exports = {
  STATUS_CONTEXT,
  evaluateReview,
  refreshPull
});
