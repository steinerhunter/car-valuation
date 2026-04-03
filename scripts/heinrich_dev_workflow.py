#!/usr/bin/env python3
"""
Heinrich Multi-Agent Development Workflow Manager
===============================================

Master script that orchestrates the complete development workflow:
1. Feature development
2. PR creation  
3. Code review agent spawning
4. Review processing
5. Merge management

Usage:
    python heinrich_dev_workflow.py start "feature-name" "description"
    python heinrich_dev_workflow.py review "pr-url" 
    python heinrich_dev_workflow.py merge "branch-name"
"""

import sys
import json
import subprocess
import os
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

class HeinrichWorkflow:
    def __init__(self, project_path=None):
        self.project_path = Path(project_path or "/home/omer/.openclaw/workspace/skills/car-valuation")
        self.workflow_state = self.project_path / ".workflow_state.json"
        
    def start_feature(self, feature_name, description):
        """Start new feature development workflow"""
        print(f"🚀 Starting feature development: {feature_name}")
        
        # Create feature branch
        branch_name = f"feature/{feature_name}"
        self._run_git(["checkout", "main"])
        self._run_git(["pull"])
        self._run_git(["checkout", "-b", branch_name])
        
        # Save workflow state
        state = {
            "feature_name": feature_name,
            "description": description,
            "branch_name": branch_name,
            "status": "development",
            "created_at": datetime.now().isoformat(),
            "commits": []
        }
        self._save_state(state)
        
        print(f"✅ Created branch: {branch_name}")
        print(f"📝 Ready for development: {description}")
        print(f"💡 When ready, commit with: python {__file__} commit 'commit message'")
        
        return branch_name
    
    def commit_changes(self, commit_message, files=None):
        """Commit changes with workflow tracking"""
        state = self._load_state()
        if not state:
            print("❌ No active workflow. Start with: python {__file__} start 'feature-name'")
            return False
            
        # Add files
        if files:
            for file in files:
                self._run_git(["add", file])
        else:
            self._run_git(["add", "."])
        
        # Enhanced commit message
        enhanced_message = f"""{commit_message}

🤖 Heinrich Development Workflow:
- Feature: {state['feature_name']}
- Branch: {state['branch_name']}
- Status: Ready for Review
- Timestamp: {datetime.now().isoformat()}

Co-authored-by: Heinrich AI <heinrich@heinrich.bot>"""
        
        self._run_git(["commit", "-m", enhanced_message])
        
        # Update state
        state["commits"].append({
            "message": commit_message,
            "timestamp": datetime.now().isoformat()
        })
        state["status"] = "committed"
        self._save_state(state)
        
        print(f"✅ Committed: {commit_message}")
        print(f"📋 Next step: python {__file__} create-pr")
        
        return True
    
    def create_pull_request(self):
        """Create PR and spawn review agent"""
        state = self._load_state()
        if not state or state["status"] not in ["committed", "development"]:
            print("❌ No commits to create PR from")
            return False
        
        branch_name = state["branch_name"]
        feature_name = state["feature_name"]
        description = state["description"]
        
        # Push branch
        self._run_git(["push", "-u", "origin", branch_name])
        
        # Create comprehensive PR description
        pr_description = self._generate_pr_description(state)
        
        # Try to create PR using gh CLI
        try:
            pr_cmd = [
                "gh", "pr", "create",
                "--title", f"🧠 {feature_name.replace('-', ' ').title()}",
                "--body", pr_description,
                "--head", branch_name,
                "--base", "main"
            ]
            result = subprocess.run(pr_cmd, cwd=self.project_path, 
                                  capture_output=True, text=True, check=True)
            pr_url = result.stdout.strip()
            
            # Update state with PR info
            state["pr_url"] = pr_url
            state["status"] = "pr_created"
            self._save_state(state)
            
            print(f"✅ PR Created: {pr_url}")
            
            # Automatically spawn review agent
            self.spawn_review_agent(pr_url)
            
            return pr_url
            
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("⚠️ Could not create PR automatically.")
            print("Please create manually and then run:")
            print(f"python {__file__} review 'PR_URL'")
            return None
    
    def spawn_review_agent(self, pr_url=None):
        """Spawn dedicated code review agent"""
        state = self._load_state()
        if not pr_url:
            pr_url = state.get("pr_url") if state else None
            
        if not pr_url:
            print("❌ No PR URL available for review")
            return False
        
        print(f"🔍 Spawning Code Review Agent for: {pr_url}")
        
        # Generate review prompt
        review_prompt = self._generate_review_prompt(state, pr_url)
        
        # Save review request to file for sessions_spawn to pick up
        review_request = {
            "pr_url": pr_url,
            "prompt": review_prompt,
            "feature": state["feature_name"] if state else "unknown",
            "timestamp": datetime.now().isoformat()
        }
        
        review_file = self.project_path / f".review_request_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(review_file, 'w') as f:
            json.dump(review_request, f, indent=2)
        
        print(f"📋 Review request saved: {review_file}")
        print(f"🤖 To spawn agent manually, run:")
        print(f"   sessions_spawn task='{review_prompt[:100]}...' label='code-review-{state['feature_name'] if state else 'manual'}'")
        
        return True
    
    def _generate_pr_description(self, state):
        """Generate comprehensive PR description"""
        changed_files = self._get_changed_files()
        
        return f"""{state['description']}

## 🔄 Multi-Agent Development Process

**Development Agent:** Heinrich AI  
**Feature:** {state['feature_name']}  
**Branch:** `{state['branch_name']}`  
**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

## 📊 Development Summary
**Commits:** {len(state.get('commits', []))}  
**Files Changed:** {len(changed_files)} files

## 📁 Files Modified
{chr(10).join(f'- `{file}`' for file in changed_files)}

## 🔍 Review Requirements

### 🎯 Code Review Checklist
- [ ] **Architecture**: Follows project patterns and best practices
- [ ] **Security**: No vulnerabilities, proper input validation
- [ ] **Performance**: Efficient algorithms, minimal API calls
- [ ] **Bug Prevention**: Edge cases handled, error handling present
- [ ] **Code Quality**: Clear names, single responsibility, DRY
- [ ] **Domain Logic**: Hebrew handling, Israeli market accuracy
- [ ] **Documentation**: Interfaces documented, complex logic explained

### 🇮🇱 Domain-Specific Validation
- [ ] Hebrew text processing correct
- [ ] Yad2 integration robust and error-resistant
- [ ] Israeli market logic accurate
- [ ] Currency formatting proper (₪)
- [ ] Geographic data valid (cities, regions)

## 🤖 Review Agent Instructions

**Code Review Agent:** Please analyze this PR comprehensively:

1. **Use `read` tool** to examine all changed files
2. **Check architecture** against existing patterns
3. **Verify security** - no hardcoded secrets, proper validation
4. **Assess performance** - efficient algorithms, API usage
5. **Review domain logic** - Hebrew handling, market accuracy
6. **Suggest simplifications** where complex code can be cleaner

**Decision Required:**
- ✅ **APPROVED** - Ready to merge
- ❌ **CHANGES REQUESTED** - Issues must be addressed

## 📋 Merge Criteria
- Review Agent approval required
- All security concerns addressed
- Performance acceptable
- Domain logic validated
- Code complexity reasonable

---
**🎩 Heinrich AI Multi-Agent Development Workflow v1.0**"""
    
    def _generate_review_prompt(self, state, pr_url):
        """Generate comprehensive review prompt for spawned agent"""
        changed_files = self._get_changed_files()
        
        return f"""🔍 CODE REVIEW MISSION - Heinrich Multi-Agent Workflow

You are the **Code Review Agent** for Heinrich's development workflow.

## 📋 Your Task:
Perform COMPREHENSIVE code review of: {pr_url}

## 🎯 Feature Context:
**Feature:** {state['feature_name'] if state else 'Manual Review'}
**Description:** {state['description'] if state else 'No description provided'}
**Files Changed:** {len(changed_files)} files

## 🔧 Required Actions:

### 1. **READ THE CODE** 
Use `read` tool to examine these files:
{chr(10).join(f'- {file}' for file in changed_files)}

### 2. **COMPREHENSIVE ANALYSIS**
Check each area thoroughly:

**🏗️ Architecture & Design:**
- Does code follow existing project patterns?
- Is separation of concerns maintained?
- Are abstractions appropriate and consistent?

**🔒 Security Analysis:**
- Any hardcoded secrets or credentials?
- Proper input validation and sanitization?
- SQL injection or XSS vulnerabilities?
- Sensitive data exposure risks?

**⚡ Performance Review:**
- Efficient algorithms and data structures?
- Minimal and optimized API calls?
- Proper resource management?
- Potential bottlenecks or blocking operations?

**🐛 Bug Prevention:**
- Edge cases handled properly?
- Comprehensive error handling?
- Resource cleanup (files, connections)?
- Race conditions or threading issues?

**🧹 Code Simplification:**
- Overly complex functions that can be simplified?
- Repeated code patterns (DRY violations)?
- Unclear or misleading variable names?
- Functions doing too many things?

**🇮🇱 Domain-Specific (Israeli Car Market):**
- Hebrew text handling correct and robust?
- Yad2 scraping logic sound and error-resistant?
- Israeli market calculations accurate?
- Currency formatting proper (₪ symbols, amounts)?
- Geographic data valid (Israeli cities/regions)?

### 3. **PROVIDE SPECIFIC FEEDBACK**
For any issues found:
- Reference exact **file:line** locations
- Explain the **problem clearly**
- Provide **concrete solution suggestions**
- Assess **severity level** (critical/major/minor)

### 4. **FINAL DECISION**
Output your final decision clearly:

**If approved:**
```
✅ APPROVED - Ready for Merge

## ✨ Review Summary:
- Architecture: ✅ Follows patterns
- Security: ✅ No vulnerabilities found
- Performance: ✅ Efficient implementation
- Bug Prevention: ✅ Proper error handling
- Code Quality: ✅ Clean and readable
- Domain Logic: ✅ Israeli market accurate

This PR meets all quality standards and is ready to merge!
```

**If changes needed:**
```
❌ CHANGES REQUESTED

## 🐛 Issues Found:
1. **[File:Line]** - [Specific issue] 
   💡 **Suggestion:** [Concrete fix]
   🔴 **Severity:** [Critical/Major/Minor]

2. **[File:Line]** - [Another issue]
   💡 **Suggestion:** [Concrete fix]
   🔴 **Severity:** [Critical/Major/Minor]

## 📋 Next Steps:
- Address all Critical and Major issues
- Consider Minor improvements
- Re-request review when ready
```

## ⚠️ CRITICAL: 
Heinrich's code quality depends on your thorough review. Take time to examine each file carefully. Look for not just obvious bugs, but subtle issues, security vulnerabilities, and opportunities for improvement.

**BEGIN YOUR COMPREHENSIVE REVIEW NOW.**"""
    
    def _run_git(self, cmd):
        """Run git command safely"""
        return subprocess.run(["git"] + cmd, cwd=self.project_path, check=True)
    
    def _get_changed_files(self):
        """Get list of changed files"""
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", "main...HEAD"],
                cwd=self.project_path, capture_output=True, text=True
            )
            return [f for f in result.stdout.strip().split('\n') if f]
        except:
            return []
    
    def _load_state(self):
        """Load workflow state"""
        try:
            if self.workflow_state.exists():
                return json.loads(self.workflow_state.read_text())
        except:
            pass
        return None
    
    def _save_state(self, state):
        """Save workflow state"""
        self.workflow_state.write_text(json.dumps(state, indent=2))

def main():
    if len(sys.argv) < 2:
        print("Heinrich Multi-Agent Development Workflow")
        print("\nUsage:")
        print("  start <feature-name> <description>  - Start new feature")
        print("  commit <message>                    - Commit changes")
        print("  create-pr                          - Create PR and spawn reviewer")
        print("  review <pr-url>                    - Spawn review agent")
        print("  status                             - Show current workflow status")
        return
    
    workflow = HeinrichWorkflow()
    command = sys.argv[1]
    
    if command == "start" and len(sys.argv) >= 4:
        feature_name = sys.argv[2]
        description = " ".join(sys.argv[3:])
        workflow.start_feature(feature_name, description)
        
    elif command == "commit" and len(sys.argv) >= 3:
        message = " ".join(sys.argv[2:])
        workflow.commit_changes(message)
        
    elif command == "create-pr":
        workflow.create_pull_request()
        
    elif command == "review" and len(sys.argv) >= 3:
        pr_url = sys.argv[2]
        workflow.spawn_review_agent(pr_url)
        
    elif command == "status":
        state = workflow._load_state()
        if state:
            print(f"📊 Current Feature: {state['feature_name']}")
            print(f"🌿 Branch: {state['branch_name']}")
            print(f"📈 Status: {state['status']}")
            if 'pr_url' in state:
                print(f"🔗 PR: {state['pr_url']}")
        else:
            print("📭 No active workflow")
    
    else:
        print("❌ Invalid command or missing arguments")

if __name__ == "__main__":
    main()