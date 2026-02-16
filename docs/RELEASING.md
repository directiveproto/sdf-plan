# Releasing

This project uses tag-based releases and Trusted Publishing to PyPI.

## Versioning

1. Update version in `pyproject.toml`.
2. Add a matching entry in `CHANGELOG.md`.
3. Commit changes to `main`.

## Tag and Publish

1. Create tag:
```bash
git tag vX.Y.Z
git push origin vX.Y.Z
```
2. GitHub Actions `release.yml` runs:
- test matrix
- build
- PyPI publish

## GitHub Release Notes

Create a GitHub Release for each tag with notes aligned to `CHANGELOG.md`.

Example:
```bash
gh release create vX.Y.Z \
  --repo directiveproto/sdf-plan \
  --title "vX.Y.Z" \
  --notes-file /path/to/release-notes.md
```

## Notes Requirements

Release notes should include:
1. Key changes/fixes for that version.
2. Any compatibility or migration notes.
3. Known limitations, if any.

## Validation

After publish:
1. Verify PyPI has both wheel and sdist.
2. Verify GitHub Release exists for the same tag.
3. Verify README badges and links resolve.
