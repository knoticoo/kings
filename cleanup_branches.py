#!/usr/bin/env python3
"""
GitHub Branch Cleanup Script
This script will help clean up all branches except subuser-system and make it the main branch
"""

import subprocess
import sys
import os

def run_command(cmd, check=True):
    """Run a git command and return the result"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=check)
        return result.stdout.strip(), result.stderr.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {cmd}")
        print(f"Error: {e.stderr}")
        return None, e.stderr

def get_current_branch():
    """Get current branch name"""
    stdout, stderr = run_command("git branch --show-current")
    return stdout

def get_all_branches():
    """Get all local and remote branches"""
    stdout, stderr = run_command("git branch -a")
    if stdout:
        branches = [line.strip() for line in stdout.split('\n') if line.strip()]
        return branches
    return []

def merge_branch(source_branch, target_branch="main"):
    """Merge source branch into target branch"""
    print(f"🔄 Merging {source_branch} into {target_branch}...")
    
    # Switch to target branch
    stdout, stderr = run_command(f"git checkout {target_branch}")
    if stderr and "error" in stderr.lower():
        print(f"❌ Failed to checkout {target_branch}: {stderr}")
        return False
    
    # Merge source branch
    stdout, stderr = run_command(f"git merge {source_branch} --no-ff -m 'Merge {source_branch} into {target_branch}'")
    if stderr and "error" in stderr.lower():
        print(f"❌ Failed to merge {source_branch}: {stderr}")
        return False
    
    print(f"✅ Successfully merged {source_branch} into {target_branch}")
    return True

def delete_local_branch(branch_name):
    """Delete a local branch"""
    if branch_name.startswith('*') or branch_name in ['main', 'master']:
        return True  # Skip current branch and main/master
    
    print(f"🗑️  Deleting local branch: {branch_name}")
    stdout, stderr = run_command(f"git branch -D {branch_name}", check=False)
    if stderr and "error" in stderr.lower():
        print(f"⚠️  Could not delete {branch_name}: {stderr}")
        return False
    return True

def delete_remote_branch(branch_name):
    """Delete a remote branch"""
    if branch_name.startswith('remotes/origin/'):
        branch_name = branch_name.replace('remotes/origin/', '')
    
    if branch_name in ['main', 'master', 'HEAD']:
        return True  # Skip main/master and HEAD
    
    print(f"🗑️  Deleting remote branch: {branch_name}")
    stdout, stderr = run_command(f"git push origin --delete {branch_name}", check=False)
    if stderr and "error" in stderr.lower():
        print(f"⚠️  Could not delete remote {branch_name}: {stderr}")
        return False
    return True

def main():
    """Main cleanup function"""
    print("🧹 GitHub Branch Cleanup Script")
    print("=" * 40)
    
    # Check if we're in a git repository
    if not os.path.exists('.git'):
        print("❌ Not in a git repository")
        return False
    
    # Get current branch
    current_branch = get_current_branch()
    print(f"📍 Current branch: {current_branch}")
    
    # Get all branches
    all_branches = get_all_branches()
    print(f"📋 Found {len(all_branches)} branches")
    
    # Show branches
    print("\n📋 All branches:")
    for branch in all_branches:
        print(f"  - {branch}")
    
    # Ask for confirmation
    print("\n⚠️  This will:")
    print("  1. Merge feature/subuser-system into main")
    print("  2. Delete all other local branches")
    print("  3. Delete all other remote branches")
    print("  4. Keep only main branch")
    
    response = input("\nContinue? (y/N): ").strip().lower()
    if response != 'y':
        print("❌ Operation cancelled")
        return False
    
    # Step 1: Merge subuser-system into main
    if current_branch != 'main':
        if not merge_branch('feature/subuser-system', 'main'):
            print("❌ Failed to merge branches")
            return False
    
    # Step 2: Delete local branches
    print("\n🗑️  Deleting local branches...")
    local_branches = [b for b in all_branches if not b.startswith('remotes/')]
    for branch in local_branches:
        delete_local_branch(branch)
    
    # Step 3: Delete remote branches
    print("\n🗑️  Deleting remote branches...")
    remote_branches = [b for b in all_branches if b.startswith('remotes/origin/')]
    for branch in remote_branches:
        delete_remote_branch(branch)
    
    # Step 4: Push main branch
    print("\n📤 Pushing main branch...")
    stdout, stderr = run_command("git push origin main --force")
    if stderr and "error" in stderr.lower():
        print(f"⚠️  Push warning: {stderr}")
    
    # Step 5: Set main as default branch (this needs to be done on GitHub)
    print("\n🎯 Cleanup completed!")
    print("\n📋 Next steps:")
    print("1. Go to GitHub repository settings")
    print("2. Change default branch to 'main'")
    print("3. Delete any remaining branches manually if needed")
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
