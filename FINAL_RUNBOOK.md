# The Naughty Duo — Release Candidate Runbook

## Release status

This is the feature-freeze candidate for the current workflow. After this checkpoint, limit changes to verified bug fixes, security fixes, and platform/API compatibility updates. No software can be guaranteed to need no future changes: provider APIs, credentials, policies, and operating environments can change.

The default workflow prepares a plan and reports quality blockers. It does not generate video files through Google Flow by itself, and a dry run is never a real upload. Live publishing must remain disabled until credentials, source videos, platform configuration, and every quality check are verified.

## One-time check

From PowerShell:

```powershell
Set-Location C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine
python --version
python -m pytest -q
```

## Safe daily run

Start the complete local suite and dashboard:

```powershell
python scripts/run_full_social_media_suite.py --max-videos 3
```

Open `http://127.0.0.1:8088` in a browser. The console starts in dry-run mode. It writes the latest job queue to `data/ops_command_center_status.json`. Stop the dashboard with `Ctrl+C`.

## One-command Flow production monitor

Start the dashboard, live credit monitor, and guarded serial scene-generation loop together:

```powershell
python C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\scripts\start_everything.py
```

The launcher uses the existing default Brave profile (`%LOCALAPPDATA%\BraveSoftware\Brave-Browser\User Data`) via a localhost-only CDP endpoint; it does not open or copy cookies to an isolated profile. It selects only the configured Google identity from accounts already signed in to that profile, then verifies the account and project. If Brave is already running without CDP, close it normally and run the command again. When no Brave window is open, the launcher starts the same pinned default profile with local CDP enabled. It updates `data/flow_credit_status.json` and SQLite, and polls every five minutes while fewer than 10 credits are available. Refresh is verified from a new live balance read, not assumed from the clock. Generation remains limited to the single configured production account; the runner never cycles through free accounts to use their quotas. Scenes are submitted serially; after each confirmed render the balance is checked again, and uncertain/failed generation pauses for review.

The launcher only claims scenes whose stories are `QUEUED` or `PARTIAL`. Social publishing is not automatic: platform credentials, quality review, and an explicit operator approval remain required. Do not treat dashboard startup or a generated plan as a published video. Stop the monitor with `Ctrl+C`.

## YouTube and TikTok channel doctor

Run the evidence-based channel audit:

```powershell
python C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\scripts\run_channel_doctor.py
```

For a read-only live audit of the signed-in pinned Brave Studio sessions, run:

```powershell
python C:\TheNaughtyDuo_Automation\the-naughty-duo-autonomous-content-engine\scripts\run_channel_doctor.py --live-studio
```

It writes `data/channel_doctor_report.json`. To use manually exported metrics instead, provide a JSON file shaped like `{"youtube":{"as_of":"2026-10-07","videos":[{"title":"...","views":0,"average_view_duration_seconds":0,"average_percentage_viewed":0,"shown_in_feed":0,"viewed_vs_swiped_away":0}]},"tiktok":{"as_of":"2026-10-07","videos":[{"title":"...","views":0,"duration_seconds":70,"average_watch_time_seconds":0,"full_video_watch_rate":0,"shares":0}]}}` with `--studio-export <path>`. Unsupported/missing data is explicitly reported as unavailable, not as zero performance.

The doctor supports an explicit action-plan file. Dry-run is the default:

```powershell
python scripts/run_channel_doctor.py --live-studio --actions data/channel_doctor_actions.json
```

Only to apply a previously reviewed action plan live:

```powershell
python scripts/run_channel_doctor.py --live-studio --actions data/channel_doctor_actions.json --execute-actions
```

The JSON must contain an `actions` array. Metadata actions require an exact platform video ID and current title; only YouTube title, description, and tags are editable. TikTok Studio does not expose existing-post caption editing, so that operation is explicitly blocked. Permanent deletion requires an exact `DELETE <platform> <video_id>` confirmation and either an official policy-notice reference or a verified duplicate pair. Duplicate deletion also requires both local original source files to have identical SHA-256 fingerprints and both live posts to match their plan. Protected YouTube video IDs cannot be deleted. Empty/missing evidence, channel/account mismatch, changed titles, failed identity checks, or uncertain platform confirmations stop the action. Paid promotion is not supported. Action plans are not generated automatically from weak performance signals; low views or a repeated title alone are not grounds to edit/delete.

TikTok's uploader attaches to pinned Brave instead of starting a separate headless profile. The configured handle `@thenaughtyduoofficial` was verified in TikTok Studio, and an account-bound dry run passed without attaching or publishing a video. Post-management waits for the selected post row to render and compares captions after harmless Unicode and whitespace normalization. Live upload requires the persistent approval file and rechecks Studio identity. Existing-post caption edits are unsupported by TikTok Studio; evidence-qualified deletes are available only through an explicit action plan.

The legacy isolated-profile helper is not used by the one-command pinned-Brave runner. The runner expects the configured Google account to be signed in to the pinned Brave profile and verifies the account before reading credits or generating.

The helper below is for legacy workflows only; it opens a separate browser profile and is not required by the pinned-Brave runner.

```powershell
python scripts/open_flow_automation_profile.py --slot 0
```

Production uses only `google_flow.production_slot` (currently `4`) to avoid opening many account profiles. If its Google Flow quota is exhausted, generation pauses until that account's quota resets; it does not switch accounts to get around free-tier limits. Flow project IDs are opened at `https://flow.google.com/project/<project-id>`; the site's `/u/` index is not the same as this system's account slot.

To only generate the daily plan without starting the dashboard:

```powershell
python scripts/run_daily_social_media_cycle.py --max-videos 3
```

## Readiness and live publishing

Use the live readiness check to see missing prerequisites:

```powershell
python scripts/activate_live_production.py --max-videos 3
```

The persistent approval is recorded in `config/live_publish_approved.txt`. YouTube OAuth token and client-secret files are configured. TikTok uses the configured handle and pinned Brave session (not a separate `tiktok_session.json`); its uploader verifies the visible account before an action. The live gate checks local file presence and explicit approval; it does not guarantee that a platform will accept a post.

The discovered Google OAuth client is `..\client_secrets.json`. YouTube OAuth has already been authorized and the configured channel verified. Never send OAuth files, passwords, or verification codes in chat.

Never run a live command against an unreviewed batch. Resolve `BLOCKED_QA`, `BLOCKED_MISSING_VIDEO`, and `FAILED` jobs before retrying. Verify every post in the official platform dashboard.
If Flow reports an uncertain result after a prompt was submitted (for example, render may exist but download failed), the job is held for manual review and must not be retried automatically. Check the existing Flow project first so the same prompt is not submitted twice.
If a generation attempt fails before a local download is confirmed, the auto-runner pauses rather than rapidly retrying scenes. Review the Flow project and runner log before restarting.

## Status meanings

- `planned`: content plan exists; source video is not present.
- `generated`: source video exists but has not passed QA.
- `qc_passed`: source video passed all configured checks.
- `blocked`: QA, source asset, credential, approval, or upload failure prevents publishing.
- `published`: platform adapter confirmed a successful live upload.
- `DRY_RUN_ONLY`: the operation was not uploaded; this must never be described as published.

## Viral performance expectations

The system can test hooks, pacing, metadata, and posting windows, then use actual audience analytics to inform future experiments. It cannot guarantee virality, billions of views, monetization, or a specific posting time that is best for every audience. Review retention, average watch duration, viewed-vs-swiped-away, and engagement in platform analytics and adapt based on observed results.
