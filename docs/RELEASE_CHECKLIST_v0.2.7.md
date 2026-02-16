# Release Checklist: v0.2.7

Run these steps from your real git clone of `directiveproto/sdf-plan` (the folder with `.git`).

## 1) Sync and verify branch

```bash
git checkout main
git pull
```

## 2) Ensure release files are present

- `pyproject.toml` has `version = "0.2.7"`
- `CHANGELOG.md` has `## 0.2.7 - 2026-02-16`
- `docs/RELEASE_NOTES_v0.2.7.md` exists

## 3) Clean build + checks

```bash
python -m build --outdir dist_027
python -m twine check dist_027/*
python -m pip install --force-reinstall dist_027/sdf_plan-0.2.7-py3-none-any.whl
python -c "import sdf_plan; print(sdf_plan.__version__)"
python -m sdf_plan --help
```

Expected:
- twine check passes
- printed version is `0.2.7`

## 4) Commit and tag

```bash
git add pyproject.toml CHANGELOG.md src/sdf_plan/compat.py docs/RELEASE_NOTES_v0.2.7.md .github/workflows/ci.yml .github/workflows/release.yml docs/RELEASE_CHECKLIST_v0.2.7.md
git commit -m "Prepare v0.2.7 release"
git tag v0.2.7
```

## 5) Push and publish

```bash
git push origin main
git push origin v0.2.7
```

This triggers GitHub Actions `release.yml` (Trusted Publishing to PyPI).

## 6) GitHub Release notes

Use `docs/RELEASE_NOTES_v0.2.7.md` as the release notes body.

## 7) Post-release verification

```bash
pip install -U sdf-plan==0.2.7
python -c "import sdf_plan; print(sdf_plan.__version__)"
python -m sdf_plan --help
```

