# Documentation Directory

This directory contains project documentation organized by category.

## Directory Structure

### 📊 `/coverage` - Test Coverage Documentation
Contains all test coverage reports, milestones, and improvement guides.

**Files:**
- `COVERAGE_PROGRESS_SUMMARY.md` - Overall coverage progress tracking
- `COVERAGE_MILESTONE_*.md` - Coverage milestone reports (52%, 55%, 56%, 61%, 62%)
- `COVERAGE_IMPROVEMENT_GUIDE.md` - Guide for improving test coverage
- `COVERAGE_ACHIEVEMENT_56.md` - Achievement report for 56% milestone
- `COVERAGE_ACTUAL_REPORT.md` - Detailed coverage analysis
- `COVERAGE_FINAL_SUMMARY.md` - Final summary of coverage improvements

**Current Status:** 62.26% coverage with 491 passing tests

### 🔧 `/ci-cd` - CI/CD Documentation
Contains documentation about continuous integration, testing, and deployment.

**Files:**
- `CI_CD_SETUP_SUMMARY.md` - CI/CD pipeline setup and configuration
- `HIGH_PRIORITY_CICD_IMPLEMENTATION.md` - High-priority CI/CD improvements
- `INTEGRATION_TEST_OPTIMIZATION_SUMMARY.md` - Integration test optimization
- `SELECTIVE_TESTING_CHANGES.md` - Selective testing system documentation
- `CHAT_CLEANUP_IMPLEMENTATION.md` - Chat test cleanup mechanism

**Key Features:**
- Selective integration testing (70-85% test reduction)
- Pre-commit hooks
- Coverage gating (60% threshold)
- Automated dependency updates

### 📦 `/releases` - Release Documentation
Contains release notes, fixes, and version-specific documentation.

**Files:**
- `RELEASE_READINESS_SUMMARY.md` - Release readiness checklist
- `FIX_0.1.999_RELEASE.md` - Fix for version 0.1.999 issue
- `DEPRECATION_FIX_SUMMARY.md` - Deprecation fixes
- `GITHUB_PAGES_FIX_SUMMARY.md` - GitHub Pages deployment fixes
- `QUICK_FIX_PAGES.md` - Quick fixes for Pages

### 🗄️ `/archived` - Archived Documentation
Contains older documentation that is no longer actively maintained but kept for reference.

**Files:**
- `AGENTS_UPDATE_SUMMARY.md` - Agent system updates
- `WORKFLOW_AUDIT_REPORT.md` - Workflow audit findings
- `WORKFLOW_FIXES_SUMMARY.md` - Workflow fixes summary

## Quick Links

### For Developers
- [Coverage Improvement Guide](coverage/COVERAGE_IMPROVEMENT_GUIDE.md)
- [CI/CD Setup](ci-cd/CI_CD_SETUP_SUMMARY.md)
- [Selective Testing Guide](../.github/SELECTIVE_TESTING_GUIDE.md)

### For Contributors
- [Pre-commit Guide](../.github/PRE_COMMIT_GUIDE.md)
- [Testing Quick Reference](../.github/TESTING_QUICK_REFERENCE.md)
- [CI/CD Improvements](ci-cd/HIGH_PRIORITY_CICD_IMPLEMENTATION.md)

### For Project Managers
- [Coverage Progress](coverage/COVERAGE_PROGRESS_SUMMARY.md)
- [Latest Milestone](coverage/COVERAGE_MILESTONE_62_FINAL.md)
- [Release Readiness](releases/RELEASE_READINESS_SUMMARY.md)

## Documentation Standards

### Coverage Documentation
- Milestone reports should include: previous/current coverage, improvements, test counts
- Use consistent naming: `COVERAGE_MILESTONE_XX.md` where XX is the percentage
- Include both achievements and next steps

### CI/CD Documentation
- Document all workflow changes
- Include before/after comparisons
- Provide troubleshooting guides

### Release Documentation
- Follow semantic versioning
- Document breaking changes
- Include migration guides when needed

## Maintenance

### Adding New Documentation
1. Place in appropriate category directory
2. Update this README with a brief description
3. Link from relevant project documentation

### Archiving Documentation
Move outdated documentation to `/archived` with a note about when and why it was archived.

## Related Documentation

- Main project README: [../README.md](../README.md)
- Agent development guide: [../AGENTS.md](../AGENTS.md)
- Changelog: [../CHANGELOG.md](../CHANGELOG.md)
- GitHub workflows: [../.github/workflows/](../.github/workflows/)
