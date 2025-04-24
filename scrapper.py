import requests
import os
import sys
from dotenv import load_dotenv


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


params = {
    "q": f"{FRAMEWORK} stars:>10",  
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
while True:
    write_and_print(f"Fetching page {params['page']}...")
    write_and_print(f"Sending request to GitHub API...")
    response = requests.get(url, params=params, headers=headers)
    
    write_and_print(f"Response status code: {response.status_code}")
    
    if response.status_code == 200:
        write_and_print(f"Successfully received data from GitHub")
        data = response.json()
        repositories = data.get("items", [])
        total_count = data.get("total_count", 0)
        
        write_and_print(f"Total repositories matching criteria: {total_count}")
        write_and_print(f"Processing {len(repositories)} repositories from page {params['page']}...")
        all_repositories.extend(repositories)
        
        write_and_print(f"Retrieved {len(repositories)} repositories from page {params['page']}.")
        
        for i, repo in enumerate(repositories, 1):
            write_and_print(f"\nProcessing repository {i}/{len(repositories)} on page {params['page']}")
            write_and_print(f"Repository: {repo['name']}")
            write_and_print(f"Owner: {repo['owner']['login']}")
            write_and_print(f"Description: {repo.get('description', 'No description')}")
            write_and_print(f"Stars: {repo['stargazers_count']}")
            write_and_print(f"Forks: {repo['forks_count']}")
            write_and_print(f"URL: {repo['html_url']}")
            write_and_print(f"Last updated: {repo['updated_at']}")
        
        if len(repositories) < params["per_page"]:
            write_and_print(f"No more pages available, search completed")
            break
        else:
            params["page"] += 1
            write_and_print(f"Moving to page {params['page']}...")
    else:
        write_and_print(f"Error: {response.status_code}, {response.text}")
        break

write_and_print(f"\nSearch completed")
write_and_print(f"Total repositories retrieved: {len(all_repositories)}")
write_and_print(f"Closing output file...")

f.close()

# Use direct print for messages after file is closed
print(f"Results saved to {output_file}")
print(f"Script execution completed")