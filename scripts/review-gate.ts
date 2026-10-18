/** Convert the trusted Codex summary into a head-specific commit status.
 * Review thread resolution is enforced separately by GitHub branch protection.
 */
export const STATUS_CONTEXT = 'review-complete';
const CODEX_BOT = 'chatgpt-codex-connector[bot]';
const SUMMARY_MARKER = '<!-- codex-pull-request-review-summary -->';

type Status = {state: 'pending' | 'success' | 'failure'; description: string};
export type Comment = {
  id: number;
  user: {login: string; type: string} | null;
  body: string | null;
  created_at: string;
  updated_at: string;
  author_association?: string;
};
type Pull = {number: number; state: string; head: {sha: string}; base: {ref: string}};
type Repo = {owner: string; repo: string};
interface Client {
  paginate<T>(route: string, params: Record<string, unknown>): Promise<T[]>;
  rest: {
    pulls: {get(params: Repo & {pull_number: number}): Promise<{data: Pull}>};
    repos: {createCommitStatus(params: Repo & {sha: string; context: string; state: string; description: string; target_url: string}): Promise<unknown>};
  };
}

export function evaluateReview(head: string, comments: Comment[]): Status {
  const summary = comments.filter(c => c.user?.login === CODEX_BOT && c.user.type === 'Bot'
    && c.body?.includes(SUMMARY_MARKER)).sort((a, b) => b.updated_at.localeCompare(a.updated_at) || b.id - a.id)[0];
  if (!summary) return {state: 'pending', description: 'Waiting for Codex review on the latest commit'};
  const match = summary.body!.match(/<!-- codex-review-state:v1 (\{[^\n]*\}) -->/);
  if (!match) return {state: 'failure', description: 'Unknown Codex summary format; review gate needs attention'};
  let data: {code_review?: {commit_sha?: string; status?: string}; security_review?: {commit_sha?: string | null; status?: string | null}};
  try { data = JSON.parse(match[1]); }
  catch { return {state: 'failure', description: 'Invalid Codex summary; review gate needs attention'}; }
  if (!data || typeof data !== 'object') return {state: 'failure', description: 'Invalid Codex review state'};
  const review = data.code_review;
  if (!review || review.commit_sha !== head) return {state: 'pending', description: 'Latest commit has not been reviewed by Codex'};
  // A new manual request invalidates a prior completion on the same SHA.
  const request = comments.filter(c => ['OWNER', 'MEMBER', 'COLLABORATOR'].includes(c.author_association || '')
    && /(?:^|\s)@codex[ \t]+(?:security[ \t]+)?review\b/i.test(c.body || ''))
    .sort((a, b) => b.updated_at.localeCompare(a.updated_at) || b.id - a.id)[0];
  if (request && request.updated_at >= summary.updated_at) return {state: 'pending', description: 'Waiting for Codex to finish the new review request'};
  if (review.status !== 'completed') {
    return {state: ['failed', 'error', 'cancelled'].includes(review.status || '') ? 'failure' : 'pending',
      description: 'Codex code review is not completed'};
  }
  // If an additional review has been requested, it must finish as well.
  const security = data.security_review;
  if (security?.status && (security.commit_sha !== head || security.status !== 'completed')) {
    return {state: 'pending', description: 'Waiting for the requested Codex security review'};
  }
  return {state: 'success', description: 'Latest commit reviewed; all review threads must also be resolved'};
}

export async function refreshPull(github: Client, repo: Repo, number: number): Promise<Status | null> {
  const {data: pull} = await github.rest.pulls.get({...repo, pull_number: number});
  if (pull.state !== 'open' || !['dev', 'main'].includes(pull.base.ref)) return null;
  const target_url = `https://github.com/${repo.owner}/${repo.repo}/pull/${number}`;
  const post = (status: Status) => github.rest.repos.createCommitStatus({...repo, sha: pull.head.sha,
    context: STATUS_CONTEXT, target_url, ...status});
  await post({state: 'pending', description: 'Checking latest Codex review state'});
  // Pagination is necessary: a review summary may follow hundreds of comments.
  const comments = await github.paginate<Comment>('GET /repos/{owner}/{repo}/issues/{issue_number}/comments',
    {...repo, issue_number: number, per_page: 100});
  const status = evaluateReview(pull.head.sha, comments);
  const current = await github.rest.pulls.get({...repo, pull_number: number});
  // Never attach a result calculated for an older head to the new commit.
  if (current.data.head.sha !== pull.head.sha || current.data.state !== 'open') return null;
  await post(status);
  return status;
}

