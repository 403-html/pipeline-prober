import subprocess
import json
from collections import Counter
import argparse
import logging
from tqdm import tqdm

logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.INFO)

parser = argparse.ArgumentParser(description='Analyze GitHub workflow runs for common failure actions')
parser.add_argument('--owner', required=True, help='The owner of the repository')
parser.add_argument('--repo', required=True, help='The name of the repository')
parser.add_argument('--workflow', required=True, help='The name of the workflow')
parser.add_argument('--limit', type=int, default=200, help='optional, default 200, The number of workflow runs to analyze, from most recent to oldest')
args = parser.parse_args()

REPO_OWNER = args.owner
REPO_NAME = args.repo
WORKFLOW_NAME = args.workflow
LIMIT = args.limit
PER_PAGE = 100

def get_workflow_id(owner, repo, workflow_name):
    logging.debug(f"Fetching workflow ID for workflow '{workflow_name}' in repo '{owner}/{repo}'")
    result = subprocess.run(
        ['gh', 'api', f'repos/{owner}/{repo}/actions/workflows'],
        capture_output=True, text=True, check=True
    )
    workflows = json.loads(result.stdout)['workflows']
    for workflow in workflows:
        if workflow['name'] == workflow_name:
            workflow_id = workflow['id']
            logging.debug(f"Found workflow ID: {workflow_id}")
            return workflow_id
    raise ValueError(f'Workflow {workflow_name} not found')

def get_workflow_runs(owner, repo, workflow_id, limit, per_page):
    logging.debug(f"Fetching workflow runs for workflow ID '{workflow_id}', up to {limit} runs")
    page = 1
    all_runs = []
    while len(all_runs) < limit:
        logging.debug(f"Fetching page {page}")
        result = subprocess.run(
            ['gh', 'api', f'repos/{owner}/{repo}/actions/workflows/{workflow_id}/runs?per_page={per_page}&page={page}'],
            capture_output=True, text=True, check=True
        )
        runs_page = json.loads(result.stdout)['workflow_runs']
        all_runs.extend(runs_page)
        logging.debug(f"Fetched {len(runs_page)} runs, total fetched: {len(all_runs)}")
        if len(runs_page) < per_page:  # No more pages to fetch
            break
        page += 1

    all_runs = all_runs[::-1]

    if all_runs:
        first_run_date = all_runs[0]['created_at']
        last_run_date = all_runs[-1]['created_at']
        logging.info(f"First run date: {first_run_date}")
        logging.info(f"Last run date: {last_run_date}")

        return all_runs[:limit]
    else:
        raise ValueError(f"No workflow runs found for workflow ID {workflow_id}")

def analyze_failures(workflow_runs):
    logging.info("Analyzing workflow runs for failures")
    failure_reasons = []
    for run in tqdm(workflow_runs, desc="Analyzing workflow runs"):
        if run['conclusion'] == 'failure':
            jobs_url = run['jobs_url']
            result = subprocess.run(
                ['gh', 'api', jobs_url],
                capture_output=True, text=True, check=True
            )
            jobs = json.loads(result.stdout)['jobs']
            for job in jobs:
                if job['conclusion'] == 'failure':
                    for step in job['steps']:
                        if step['conclusion'] == 'failure':
                            failure_reasons.append(step['name'])
    logging.info("Analysis complete")
    return Counter(failure_reasons)

def main():
    logging.debug("Starting analysis")
    workflow_id = get_workflow_id(REPO_OWNER, REPO_NAME, WORKFLOW_NAME)
    workflow_runs = get_workflow_runs(REPO_OWNER, REPO_NAME, workflow_id, LIMIT, PER_PAGE)
    
    logging.debug("Starting failure analysis with progress bar")
    failure_counts = analyze_failures(workflow_runs)
    
    logging.info("\n------------------\nMost common failure reasons:")
    for reason, count in failure_counts.most_common():
        print(f"{reason}: {count}")

if __name__ == "__main__":
    main()