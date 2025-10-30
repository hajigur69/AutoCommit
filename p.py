import os
import random
import string
import datetime
import subprocess
import sys
import shutil
import re

# ========== KONFIGURASI ==========
REPO_URL = "https://github.com/USERNAME/REPO" 
FAKE_COMMIT_YEARS = 2  # Berapa tahun ke belakang
MAX_COMMITS_PER_DAY = 2  # Maksimal commit per hari
BRANCH = 'main'
# ========== END OF KONFIGURASI ==========

def clean_dir(path):
    if os.path.isdir(path):
        shutil.rmtree(path)

def random_lines(n):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=n))

def generate_all_days(years):
    now = datetime.datetime.now()
    start_year = now.year - years + 1
    days = []
    for year in range(start_year, now.year + 1):
        start = datetime.date(year, 1, 1)
        end = datetime.date(year, 12, 31)
        if year == now.year:
            end = now.date()
        delta = (end - start).days + 1
        for i in range(delta):
            days.append(start + datetime.timedelta(days=i))
    random.shuffle(days)
    return days

def run_git(cmd, env=None):
    result = subprocess.run(cmd, shell=True, env=env,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        print(f"Error: {result.stderr.decode()}")
    return result

def get_git_username():
    # Coba dari config git, jika gagal pakai user.name, jika gagal pakai "FakeUser"
    try:
        user = subprocess.check_output("git config user.name", shell=True).decode().strip()
        if user:
            return user
    except:
        return "FakeUser"
    return "FakeUser"

def get_git_email():
    try:
        email = subprocess.check_output("git config user.email", shell=True).decode().strip()
        if email:
            return email
    except:
        return "fakeuser@example.com"
    return "fakeuser@example.com"

def extract_dir_from_url(repo_url):
    # Ambil nama repo dari url, contoh: https://github.com/user/fake-contributions-repo.git
    match = re.search(r'/([^/]+?)(\.git)?$', repo_url)
    if match:
        return match.group(1)
    return "repo"

def main():
    print(f"== FAKE GITHUB CONTRIBUTION TOOL ==")
    print(f"Repo URL: {REPO_URL}")
    print(f"Backdated: {FAKE_COMMIT_YEARS} year(s)")

    repo_dir = extract_dir_from_url(REPO_URL)
    clean_dir(repo_dir)
    print(f"Cloning repository...")
    run_git(f"git clone {REPO_URL}")

    if not os.path.isdir(repo_dir):
        print("Failed to clone repo.")
        sys.exit(1)
    os.chdir(repo_dir)

    # Checkout branch (ignore error if already on branch)
    run_git(f"git checkout {BRANCH}")

    git_username = get_git_username()
    git_email = get_git_email()
    print(f"Git username: {git_username}")
    print(f"Git email   : {git_email}")

    all_days = generate_all_days(FAKE_COMMIT_YEARS)
    commit_count = 0

    for day in all_days:
        num_commits = random.randint(1, MAX_COMMITS_PER_DAY)
        for _ in range(num_commits):
            line = f"Logs: {day} {random_lines(8)}\n"
            with open(".Logs", "a") as f:
                f.write(line)

            run_git(f"git add .Logs")
            commit_time = datetime.datetime.combine(day, datetime.time(
                hour=random.randint(1, 23),
                minute=random.randint(0, 59),
                second=random.randint(0, 59)
            ))
            iso = commit_time.strftime("%Y-%m-%dT%H:%M:%S")
            env = os.environ.copy()
            env["GIT_AUTHOR_NAME"] = git_username
            env["GIT_AUTHOR_EMAIL"] = git_email
            env["GIT_COMMITTER_NAME"] = git_username
            env["GIT_COMMITTER_EMAIL"] = git_email
            env["GIT_AUTHOR_DATE"] = iso
            env["GIT_COMMITTER_DATE"] = iso

            run_git(f'git commit -m "Logs on {day}"', env=env)
            commit_count += 1

    print(f"\nTotal fake commits: {commit_count}")

    print("Pushing to GitHub...")
    run_git(f"git push origin {BRANCH}")

    print("\n>>> DONE. Check your GitHub contributions graph!")

if __name__ == "__main__":
    main()
