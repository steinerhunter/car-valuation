#!/usr/bin/env python3
"""
Multi-Agent Development Workflow
================================

Automated PR creation and Code Review process using Heinrich AI agents.

Workflow:
1. Heinrich develops feature on branch
2. Creates PR with detailed description  
3. Spawns Code Review Agent
4. Review Agent analyzes code comprehensively
5. Approval/rejection with detailed feedback
6. Merge or iterate based on review
"""

import os
import json
import subprocess
from datetime import datetime
from pathlib import Path

class PRWorkflow:
    def __init__(self, repo_path):
        self.repo_path = Path(repo_path)
        self.workflow_log = self.repo_path / "workflow_log.json"
    
    def create_feature_branch(self, feature_name):
        """Create and switch to new feature branch"""
        branch_name = f"feature/{feature_name}"
        
        # Create branch from main
        subprocess.run(["git", "checkout", "main"], cwd=self.repo_path, check=True)
        subprocess.run(["git", "pull"], cwd=self.repo_path, check=True)
        subprocess.run(["git", "checkout", "-b", branch_name], cwd=self.repo_path, check=True)
        
        return branch_name
    
    def commit_changes(self, message, files=None):
        """Commit changes with proper message format"""
        if files:
            for file in files:
                subprocess.run(["git", "add", file], cwd=self.repo_path, check=True)
        else:
            subprocess.run(["git", "add", "."], cwd=self.repo_path, check=True)
        
        # Enhanced commit message with metadata
        enhanced_message = f"""{message}

🤖 Heinrich Development Log:
- Timestamp: {datetime.now().isoformat()}
- Agent: Heinrich (Development)  
- Status: Ready for Review
- Next: Code Review Agent Analysis

Co-authored-by: Heinrich AI <heinrich@heinrich.bot>"""
        
        subprocess.run(["git", "commit", "-m", enhanced_message], 
                      cwd=self.repo_path, check=True)
    
    def create_pull_request(self, title, description, branch_name):
        """Create PR with comprehensive description"""
        
        # Generate PR description template
        pr_description = f"""{description}

## 🔄 Multi-Agent Development Process

**Development Agent:** Heinrich AI  
**Branch:** `{branch_name}`  
**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

## 📋 Review Checklist

### 🔍 Code Quality
- [ ] Architecture follows project patterns
- [ ] Functions are single-purpose and clear
- [ ] Variable names are descriptive
- [ ] Comments explain 'why', not 'what'

### 🐛 Bug Prevention  
- [ ] Error handling is comprehensive
- [ ] Edge cases are handled
- [ ] Input validation is present
- [ ] Resource cleanup is proper

### ⚡ Performance
- [ ] No obvious performance bottlenecks
- [ ] Efficient algorithms and data structures
- [ ] Minimal API calls and I/O
- [ ] Proper caching where applicable

### 🧪 Testing
- [ ] Code is testable
- [ ] Critical paths have tests
- [ ] Happy path and error cases covered
- [ ] Mock dependencies appropriately

### 📚 Documentation
- [ ] Public interfaces documented
- [ ] Complex logic explained
- [ ] README updated if needed
- [ ] Examples provided where helpful

## 🤖 Review Agent Instructions

**Code Review Agent,** please analyze this PR with the following focus:

1. **Architecture Analysis**: Does this fit well with existing code?
2. **Security Review**: Any potential security issues?
3. **Performance Review**: Potential optimization opportunities?
4. **Simplification**: Can any complex code be simplified?
5. **Hebrew/Israeli Market Logic**: Specific domain correctness?

**If issues found:** Request changes with specific suggestions
**If approved:** Comment "✅ APPROVED" and this will auto-merge

## 📊 Files Changed

```
{self._get_changed_files()}
```

---
**🎩 Heinrich AI Multi-Agent Development Workflow**
"""
        
        # Push branch first
        subprocess.run(["git", "push", "-u", "origin", branch_name], 
                      cwd=self.repo_path, check=True)
        
        # Create PR using gh CLI (if available) or manual instructions
        try:
            pr_cmd = [
                "gh", "pr", "create",
                "--title", title,
                "--body", pr_description,
                "--head", branch_name,
                "--base", "main"
            ]
            result = subprocess.run(pr_cmd, cwd=self.repo_path, 
                                  capture_output=True, text=True, check=True)
            pr_url = result.stdout.strip()
            print(f"✅ PR Created: {pr_url}")
            return pr_url
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠️ gh CLI not available. Create PR manually at:")
            print(f"https://github.com/{self._get_repo_info()}/compare/{branch_name}")
            return None
    
    def spawn_review_agent(self, pr_url, code_summary):
        """Spawn dedicated Code Review Agent"""
        
        review_prompt = f"""🔍 CODE REVIEW MISSION: Comprehensive Analysis

You are the **Code Review Agent** in Heinrich's Multi-Agent Development Workflow.

## 📋 Your Task:
Perform COMPREHENSIVE code review of PR: {pr_url}

## 🎯 Analysis Required:

### 1. **Architecture Review**
- Does code follow existing patterns?
- Is separation of concerns maintained?
- Are abstractions appropriate?

### 2. **Bug Detection**
- Potential runtime errors?
- Edge cases handled?
- Resource leaks or memory issues?

### 3. **Security Analysis**
- Input validation present?
- SQL injection risks?
- Sensitive data exposure?

### 4. **Performance Review**
- Inefficient algorithms?
- Unnecessary API calls?
- Blocking operations?

### 5. **Code Simplification**
- Overly complex functions?
- Repeated code patterns?
- Unclear variable names?

### 6. **Domain-Specific (Israeli Car Market)**
- Hebrew text handling correct?
- Yad2 scraping logic sound?
- Price formatting appropriate?

## 📊 Code Summary:
{code_summary}

## 🎯 Required Output:

**If issues found:**
```
❌ CHANGES REQUESTED

## 🐛 Issues Found:
1. [Specific issue with file:line reference]
2. [Another issue with suggestion]

## 💡 Suggestions:
- [Concrete improvement suggestions]
```

**If approved:**
```
✅ APPROVED

## ✨ Review Summary:
- Architecture: ✅ Good
- Security: ✅ Safe  
- Performance: ✅ Efficient
- Simplification: ✅ Clean
- Domain Logic: ✅ Correct

This PR is ready to merge!
```

**Begin your comprehensive review now.**"""
        
        # Use sessions_spawn to create review agent
        from scripts.pr_integration import spawn_code_reviewer
        return spawn_code_reviewer(review_prompt, pr_url)
    
    def _get_changed_files(self):
        """Get list of changed files"""
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", "HEAD~1..HEAD"],
                cwd=self.repo_path, capture_output=True, text=True
            )
            return result.stdout.strip()
        except:
            return "Unable to determine changed files"
    
    def _get_repo_info(self):
        """Extract owner/repo from git remote"""
        try:
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                cwd=self.repo_path, capture_output=True, text=True
            )
            url = result.stdout.strip()
            # Extract from git@github.com:user/repo.git or https://github.com/user/repo
            if "github.com" in url:
                parts = url.split("/")[-2:]
                return f"{parts[0]}/{parts[1].replace('.git', '')}"
        except:
            pass
        return "unknown/unknown"

# Usage Example:
if __name__ == "__main__":
    workflow = PRWorkflow("/home/omer/.openclaw/workspace/skills/car-valuation")
    
    # Example workflow
    branch = workflow.create_feature_branch("advanced-market-analysis")
    workflow.commit_changes("🧠 Add advanced market analysis algorithms")
    pr_url = workflow.create_pull_request(
        "🧠 Advanced Market Analysis Engine", 
        "Implement sophisticated price analysis with confidence scoring",
        branch
    )
    
    if pr_url:
        workflow.spawn_review_agent(pr_url, "Advanced market analysis with statistical models")