# Pull Request Workflow

This repository uses a simple feature-branch workflow that keeps the main branch stable and makes changes easy to review.

## Branch strategy

- main: production-ready code
- feature/cli-polish: CLI improvements and user experience updates
- feature/api-hardening: API reliability and error-handling improvements
- feature/testing-coverage: test expansion and quality assurance

## Recommended workflow

1. Create a feature branch from main.
2. Make focused changes for one purpose only.
3. Commit clearly and keep PRs small.
4. Open a pull request into main.
5. Review, test, and merge.
6. Delete the feature branch after merge.

## Example flow

```bash
git checkout main
git pull origin main
git checkout -b feature/your-feature
# make changes
# commit changes
git push -u origin feature/your-feature
# open PR on GitHub
```

## Merge policy

- Use pull requests for all changes to main.
- Merge only after tests pass.
- Prefer squash or merge commits depending on team preference.
- Delete merged branches to keep the repository clean.

## Quality checks before merging

- Run tests: pytest -q
- Confirm the app starts locally: python app.py
- Review the diff for clarity and scope
