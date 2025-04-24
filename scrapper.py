import requests
import os
import sys
from dotenv import load_dotenv
from datetime import datetime, timedelta
import time


load_dotenv()

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
FRAMEWORK = os.environ.get("FRAMEWORK")

output_file = f"{FRAMEWORK}_repositories.txt"
f = open(output_file, "w")

def write_and_print(message):
    """Write to both console and file"""
    print(message)
    if not f.closed:
        f.write(message + "\n")
        f.flush()

if not GITHUB_TOKEN or not FRAMEWORK:
    write_and_print("Error: Missing GITHUB_TOKEN or FRAMEWORK environment variables.")
    f.close()
    exit(1)

write_and_print(f"GITHUB_TOKEN: {GITHUB_TOKEN[:4]}... (hidden for security)")
write_and_print(f"Searching for repositories with framework: {FRAMEWORK}")
write_and_print(f"Saving results to: {output_file}")
write_and_print(f"Starting GitHub API search...")


url = "https://api.github.com/search/repositories"
contributors_url_template = "https://api.github.com/repos/{owner}/{repo}/contributors"

five_years_ago = (datetime.now() - timedelta(days=5 * 365)).strftime("%Y-%m-%d")
write_and_print(f"Filtering repositories created after: {five_years_ago}")
write_and_print(f"Filtering repositories with more than 2 contributors")

params = {
    "q": f"{FRAMEWORK} stars:>10 created:>{five_years_ago}",  
    "sort": "updated",
    "order": "desc",
    "per_page": 100,  
    "page": 1,      
}


headers = {
    "Accept": "application/vnd.github.v3+json",
    "Authorization": f"Bearer {GITHUB_TOKEN}", 
}

write_and_print(f"Search query: {params['q']}")
write_and_print(f"Sort order: {params['sort']} {params['order']}")
write_and_print(f"Results per page: {params['per_page']}")


all_repositories = []
current_page = 1

try:
    while True:
        write_and_print(f"Fetching page {params['page']}...")
        write_and_print(f"Sending request to GitHub API...")
        response = requests.get(url, params=params, headers=headers)
        
        write_and_print(f"Response status code: {response.status_code}")
        current_page = params['page']
        
        if response.status_code == 200:
            write_and_print(f"Successfully received data from GitHub")
            data = response.json()
            repositories = data.get("items", [])
            total_count = data.get("total_count", 0)
            
            write_and_print(f"Total repositories matching criteria: {total_count}")
            write_and_print(f"Processing {len(repositories)} repositories from page {params['page']}...")
            
            filtered_count = 0
            for i, repo in enumerate(repositories, 1):
                write_and_print(f"Checking repository {i}/{len(repositories)} on page {params['page']}: {repo['name']}")
                
                owner = repo['owner']['login']
                repo_name = repo['name']
                contributors_url = contributors_url_template.format(owner=owner, repo=repo_name)
                
                write_and_print(f"Fetching contributors for {owner}/{repo_name}...")
                contributors_response = requests.get(contributors_url, headers=headers)
 
                remaining = int(contributors_response.headers.get('X-RateLimit-Remaining', 0))
                if remaining < 10:
                    reset_time = int(contributors_response.headers.get('X-RateLimit-Reset', 0))
                    sleep_time = max(reset_time - time.time(), 0) + 10
                    write_and_print(f"Rate limit almost reached! Sleeping for {sleep_time:.0f} seconds...")
                    time.sleep(sleep_time)
                
                if contributors_response.status_code == 200:
                    contributors = contributors_response.json()
                    contributor_count = len(contributors)
                    
                    if contributor_count > 2:
                        filtered_count += 1
                        all_repositories.append(repo)
                        created_date = repo.get('created_at', 'Unknown')
                        
                        write_and_print(f"\nIncluding repository with {contributor_count} contributors")
                        write_and_print(f"Repository: {repo['name']}")
                        write_and_print(f"Owner: {repo['owner']['login']}")
                        write_and_print(f"Description: {repo.get('description', 'No description')}")
                        write_and_print(f"Stars: {repo['stargazers_count']}")
                        write_and_print(f"Forks: {repo['forks_count']}")
                        write_and_print(f"Created at: {created_date}")
                        write_and_print(f"URL: {repo['html_url']}")
                        write_and_print(f"Last updated: {repo['updated_at']}")
                        write_and_print(f"Contributors: {contributor_count}")
                    else:
                        write_and_print(f"Skipping {repo_name} - only has {contributor_count} contributors")
                else:
                    write_and_print(f"Error fetching contributors for {repo_name}: {contributors_response.status_code}")
                    
                time.sleep(0.5)
            
            write_and_print(f"Found {filtered_count} repositories with >2 contributors on page {params['page']}")
            
            if len(repositories) < params["per_page"]:
                write_and_print(f"No more pages available, search completed")
                break
            else:
                params["page"] += 1
                write_and_print(f"Moving to page {params['page']}...")
        else:
            write_and_print(f"Error: {response.status_code}, {response.text}")
            break
except Exception as e:
    write_and_print(f"Script interrupted at page {current_page}: {str(e)}")
finally:
    write_and_print(f"\nSearch ended")
    write_and_print(f"STOPPED AT PAGE: {current_page}")
    write_and_print(f"Total repositories retrieved: {len(all_repositories)}")
    write_and_print(f"Closing output file...")
    
    f.close()

print(f"Results saved to {output_file}")
print(f"Script execution completed. Final page processed: {current_page}")
print(f"Total repositories with >2 contributors: {len(all_repositories)}")