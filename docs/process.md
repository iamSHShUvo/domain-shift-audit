# Process

How work moves from idea to merged code.

1. **Specify first.** Requirements and acceptance criteria are written in
   `SPEC.md` before any code. Each requirement becomes a GitHub Issue.
2. **Pick one issue.** Open the issue and read its acceptance criteria.
3. **Branch.** Create a branch named `issue-<number>-<short-name>`.
4. **Build.** The Builder agent implements the issue.
5. **Test.** The Tester agent writes tests for each acceptance criterion and
   runs `make test`. Nothing moves forward with failing tests.
6. **Review.** The Reviewer agent checks the diff against the issue and AGENTS.md.
7. **Pull request.** Open a pull request that references the issue
   (`Closes #N`). CI runs the tests automatically.
8. **Merge.** The human merges after CI passes. The issue closes automatically.

## Definition of done

- Every acceptance criterion in the issue is met.
- Tests exist for each criterion and `make test` passes.
- CI is green.
- The README is updated if the way to run the project changed.

## Working notes

Documentation-only changes may be committed directly to `main`.