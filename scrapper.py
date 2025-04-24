import requests
import time
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN") 
print(f"GITHUB_TOKEN: {GITHUB_TOKEN}")
HEADERS = {
    "Accept": "application/vnd.github.v3+json",
}
if GITHUB_TOKEN:
    HEADERS["Authorization"] = f"token {GITHUB_TOKEN}"
    print(f"GitHub token found and configured")
else:
    print(f"No GitHub token found. Rate limits will be restricted to 60 requests/hour")

FRAMEWORKS = [
    "nextjs",
    "react",
    "svelte",
    "remix",
    "vue",
    "angular",
    "gatsby",
    "solid"
]

INDICATOR_FILES = [
    "package.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "bun.lockb"
]

def search_repos(query, page=1, per_page=100):
    url = "https://api.github.com/search/repositories"
    params = {
        "q": query + " stars:>10",
        "sort": "stars",
        "order": "desc",
        "page": page,
        "per_page": per_page
    }
    
    print(f"  Making API request to GitHub... ({url})")
    response = requests.get(url, headers=HEADERS, params=params)
    
    if response.status_code == 200:
        data = response.json()
        total_count = data.get("total_count", 0)
        print(f"  Request successful. Found {total_count} total matches")
        return data
    elif response.status_code == 403:
        reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
        current_time = int(time.time())
        sleep_time = max(reset_time - current_time, 0) + 10
        
        print(f"  Rate limit exceeded. Waiting for {sleep_time} seconds...")
        time.sleep(sleep_time)
        return search_repos(query, page, per_page)
    else:
        print(f"  Error: {response.status_code}")
        print(f"  {response.text}")
        return {"items": []}

def get_contributors_count(repo_owner, repo_name):
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contributors"
    params = {"per_page": 3, "anon": "false"}
    
    response = requests.get(url, headers=HEADERS, params=params)
    
    if response.status_code == 200:
        contributors = response.json()
        return len(contributors)
    elif response.status_code == 403:
        reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
        current_time = int(time.time())
        sleep_time = max(reset_time - current_time, 0) + 10
        
        print(f"  Rate limit exceeded. Waiting for {sleep_time} seconds...")
        time.sleep(sleep_time)
        return get_contributors_count(repo_owner, repo_name)
    else:
        print(f"  Error getting contributors: {response.status_code}")
        return 0

def main():
    print("\n========== GitHub Framework Repository Finder ==========")
    print(f"Starting search for repositories at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Looking for {len(FRAMEWORKS)} frameworks across {len(INDICATOR_FILES)} indicator files")
    print(f"Filtering for repositories with >10 stars and ≥2 contributors")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"github_framework_repos_{timestamp}.txt"
    print(f"Results will be saved to {output_file} in real-time")
    print("======================================================\n")
    
    all_repos = []
    total_queries = len(FRAMEWORKS) * len(INDICATOR_FILES)
    current_query = 0
    
    with open(output_file, "w") as f:
        f.write(f"# GitHub Framework Repository Results\n")
        f.write(f"# Search started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"# Frameworks: {', '.join(FRAMEWORKS)}\n")
        f.write(f"# Indicator files: {', '.join(INDICATOR_FILES)}\n")
        f.write(f"# Filter: >10 stars and ≥2 contributors\n\n")
        
        for framework in FRAMEWORKS:
            print(f"\n[Framework: {framework}]")
            for indicator in INDICATOR_FILES:
                current_query += 1
                query = f"{framework} in:readme,description filename:{indicator}"
                print(f"\nQuery {current_query}/{total_queries}: {query}")
                
                for page in range(1, 6):
                    print(f"Processing page {page}...")
                    result = search_repos(query, page=page)
                    
                    if not result.get("items"):
                        print("  No items found on this page")
                        break
                    
                    new_repos = 0
                    for repo in result["items"]:
                        repo_url = repo["html_url"]
                        repo_name = repo["full_name"]
                        repo_owner, repo_short_name = repo_name.split('/')
                        stars = repo["stargazers_count"]
                        
                        if stars <= 10:
                            continue
                            
                        print(f"  Checking contributors for {repo_name}...")
                        contributors_count = get_contributors_count(repo_owner, repo_short_name)
                        print(f"  {repo_name} has {contributors_count} contributors")
                        
                        if contributors_count >= 2 and repo_url not in all_repos:
                            all_repos.append(repo_url)
                            f.write(f"{repo_url} (Stars: {stars}, Contributors: {contributors_count})\n")
                            f.flush()
                            new_repos += 1
                            
                        time.sleep(1)
                    
                    print(f"  Found {new_repos} qualifying repos on this page")
                    print(f"  Total qualifying repos so far: {len(all_repos)}")
                    
                    if len(result["items"]) < 100:
                        print("  End of results reached")
                        break
                    
                    print(f"  Pausing for 6 seconds to respect rate limits...")
                    time.sleep(6)
        
        f.write(f"\n# Search completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        f.write(f"\n# Total repositories found: {len(all_repos)}")
    
    print(f"\n======== Search Complete ========")
    print(f"Found {len(all_repos)} unique repositories with >10 stars and ≥2 contributors")
    print(f"Results saved to {output_file}")
    print(f"Finished at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=================================")

if __name__ == "__main__":
    main()
