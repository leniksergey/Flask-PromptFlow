# PromptFlow Known Bugs & Refactoring Backlog

## High Priority / Security
1. **Open Redirect:** In login/auth route handling `next` parameter, validate that the URL starts with a single `/` and does not start with `//` (prevent `//evil.example`).
2. **Scene <-> Prompt Export Leak:** `projects.export_json` and `export_markdown` currently pull *all* user prompts instead of prompts linked to the project/scenes. We need to establish a proper ForeignKey relationship between `Scene` and `Prompt` (or `PromptVersion`), and update exports.
3. **Scene Order & Unique Constraint:** Scene creation calculates `max_order + 1` before validation, potentially causing race conditions or duplicate order validation failures. Reordering scenes (`_reorder_scenes`) risks SQLite/PostgreSQL `IntegrityError` due to intermediate order updates.

## Medium Priority
4. **Prompt Versioning Optimization:** Editing prompt metadata currently creates a new version even if the text content (`body`) hasn't changed. Fix versioning logic to trigger only when text content changes.
5. **Rating Validation Flash:** Rating outside 1-5 is caught by form validation, but redirects without a user-facing flash message.
6. **Naive Datetime ISO Format:** Fix `_isoformat` timezone handling with SQLite naive datetimes.