#!/usr/bin/env python3
"""
PR Integration & Code Review Agent Spawning
===========================================

Integration layer between Heinrich development workflow and spawned review agents.
"""

import os
import subprocess
from datetime import datetime
from pathlib import Path

def spawn_code_reviewer(review_prompt, pr_url):
    """Spawn a dedicated Code Review Agent for PR analysis"""
    
    # Create unique label for this review session
    review_id = f"code-review-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    # Enhanced review prompt with strict instructions
    enhanced_prompt = f"""🎩 You are Heinrich's CODE REVIEW AGENT

{review_prompt}

## 🚨 CRITICAL INSTRUCTIONS:

1. **READ THE ACTUAL CODE**: Use the `read` tool to examine all changed files
2. **BE THOROUGH**: Don't just skim - analyze deeply
3. **BE SPECIFIC**: Reference exact lines, functions, and files
4. **SUGGEST IMPROVEMENTS**: Don't just find problems, propose solutions
5. **CHECK DOMAIN LOGIC**: Verify Israeli market, Hebrew handling, Yad2 integration
6. **PERFORMANCE FOCUS**: Look for bottlenecks, API abuse, inefficiencies

## 🔧 TOOLS AVAILABLE:
- `read` - Examine source code files
- `exec` - Test code snippets if needed  
- `web_search` - Verify best practices

## 📋 REVIEW STANDARDS:
- **Security**: No hardcoded secrets, proper input validation
- **Performance**: Efficient algorithms, minimal API calls
- **Maintainability**: Clear names, good structure, proper comments
- **Domain Accuracy**: Correct Hebrew handling, accurate market logic

Your review will determine if this code can be merged safely.

**START YOUR REVIEW NOW**"""

    try:
        # Use OpenClaw sessions_spawn to create review agent
        result_message = f"🔍 Spawning Code Review Agent for PR analysis..."
        
        # Note: This will be handled by the OpenClaw message system
        print(f"📧 Review Agent Task: {review_id}")
        print(f"📋 Task: Comprehensive code review")
        print(f"🔗 PR URL: {pr_url}")
        
        return {
            "review_id": review_id,
            "prompt": enhanced_prompt,
            "status": "spawned",
            "pr_url": pr_url
        }
        
    except Exception as e:
        print(f"❌ Failed to spawn review agent: {e}")
        return None

def extract_code_changes():
    """Extract recent code changes for review context"""
    repo_path = "/home/omer/.openclaw/workspace/skills/car-valuation"
    
    try:
        # Get changed files
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD~1..HEAD"],
            cwd=repo_path, capture_output=True, text=True, check=True
        )
        changed_files = result.stdout.strip().split('\n')
        
        # Get diff for each file
        changes_summary = {}
        for file in changed_files:
            if file and file.endswith('.py'):
                diff_result = subprocess.run(
                    ["git", "diff", "HEAD~1..HEAD", file],
                    cwd=repo_path, capture_output=True, text=True
                )
                changes_summary[file] = diff_result.stdout
        
        return changes_summary
        
    except Exception as e:
        print(f"⚠️ Could not extract changes: {e}")
        return {}

def get_review_checklist():
    """Standard checklist for code reviews"""
    return """
## 🔍 Code Review Checklist

### 🏗️ Architecture & Design
- [ ] Follows existing project patterns
- [ ] Proper separation of concerns
- [ ] Appropriate abstractions
- [ ] No tight coupling

### 🐛 Bug Prevention
- [ ] Comprehensive error handling
- [ ] Edge cases covered
- [ ] Input validation present
- [ ] Resource cleanup proper

### 🔒 Security
- [ ] No hardcoded secrets
- [ ] Proper input sanitization
- [ ] No SQL injection risks
- [ ] Sensitive data handled correctly

### ⚡ Performance
- [ ] Efficient algorithms
- [ ] Minimal API calls
- [ ] Proper caching
- [ ] No blocking operations

### 🧹 Code Quality
- [ ] Clear, descriptive names
- [ ] Single responsibility functions
- [ ] DRY principle followed
- [ ] Proper comments

### 🇮🇱 Domain-Specific
- [ ] Hebrew text handling correct
- [ ] Israeli market logic accurate
- [ ] Yad2 integration robust
- [ ] Currency formatting proper

### 📚 Documentation
- [ ] Public interfaces documented
- [ ] Complex logic explained
- [ ] Examples provided
- [ ] README updated if needed
"""

# Helper functions for the workflow
def create_review_summary(files_changed, issues_found, approval_status):
    """Create standardized review summary"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    return f"""
# 🔍 Code Review Summary
**Reviewer:** Heinrich Code Review Agent  
**Date:** {timestamp}  
**Files Reviewed:** {len(files_changed)} files

## 📊 Review Results
**Status:** {"✅ APPROVED" if approval_status else "❌ CHANGES REQUESTED"}
**Issues Found:** {len(issues_found)}

## 📁 Files Analyzed
{chr(10).join(f'- {file}' for file in files_changed)}

## 🎯 Next Steps
{
"This PR is approved for merge! 🚀" if approval_status else 
"Address the issues above and request re-review."
}

---
*Heinrich AI Multi-Agent Development Workflow*
"""

if __name__ == "__main__":
    # Test the review system
    changes = extract_code_changes()
    print("📋 Recent Changes:")
    for file, diff in changes.items():
        print(f"📝 {file}: {len(diff)} characters changed")