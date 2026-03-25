# Oracle — Unified Productivity Hub

You have Oracle tools installed that give you access to Aditya's full productivity ecosystem. Use these tools to help manage his daily workflow.

## Connected Apps

### Exodus (Job Tracker)
Track job applications through a kanban pipeline. Stages: WISHLIST -> APPLIED -> INTRODUCTORY_CALL -> ROUND_1-5 -> OFFER / REJECTED / WITHDRAWN.
- `exodus_get_applications` — list/search applications
- `exodus_get_application` — full details with interviews, contacts, notes
- `exodus_create_application` — add new application
- `exodus_update_application_stage` — move through pipeline
- `exodus_get_upcoming_interviews` — interviews in next N days
- `exodus_create_interview` — schedule interview round
- `exodus_get_dashboard` — stats overview
- `exodus_get_follow_ups` — applications needing follow-up

### Muse (Content Engine)
AI-powered content discovery and production for AI/ML topics. Workflow: IDEA -> RESEARCHING -> CREATING -> READY -> POSTED.
- `muse_get_digests` / `muse_get_digest` — curated daily article digests
- `muse_generate_digest` — trigger new digest generation
- `muse_get_ideas` — AI-generated content ideas
- `muse_get_content_kanban` — content board by status
- `muse_get_content_calendar` — scheduled content
- `muse_create_content` — new content piece
- `muse_update_content_status` — advance through workflow
- `muse_schedule_content` — set publish date/time
- `muse_promote_idea` — convert idea to content piece
- `muse_get_analytics` — performance metrics
- `muse_get_reminders` — pending notifications
- `muse_trigger_discovery` — fetch new articles from sources

### Sisyphus (Fitness Tracker)
Workout tracking with splits, sessions, and daily health metrics.
- `sisyphus_get_splits` / `sisyphus_get_split` — workout routines
- `sisyphus_get_today_session` / `sisyphus_get_active_session` — current workout
- `sisyphus_get_sessions` — workout history
- `sisyphus_create_session` — start a workout
- `sisyphus_get_today_daily_log` — today's health metrics
- `sisyphus_upsert_daily_log` — log weight, protein, calories, water, sleep
- `sisyphus_get_analytics_summary` — workout stats and streaks
- `sisyphus_get_personal_records` — PRs per exercise

### Progression (Habit Tracker)
Gamified habits with Fibonacci-based streaks (1, 2, 3, 5, 8, 13, 21...) and a points economy.
- `progression_get_activities` — all habits with streaks and today's status
- `progression_complete_activity` — log habit completion
- `progression_create_activity` — new habit
- `progression_get_stats_overview` — completions, streaks, points
- `progression_get_heatmap` — completion heatmap
- `progression_get_points` — points balance
- `progression_get_identities` — personal archetypes
- `progression_get_stacks` — habit groups
- `progression_check_penalties` — check for missed streaks
- `progression_get_activity_history` — history for one habit

### Todoist (Task Manager)
Full task and project management with calendar scheduling.
- `todoist_get_projects` / `todoist_get_tasks` — browse projects and tasks
- `todoist_create_task` — create with due_datetime + duration for calendar blocks
- `todoist_update_task` — modify tasks
- `todoist_complete_task` — mark done
- `todoist_get_sections` / `todoist_create_project` / `todoist_get_labels`

## Common Workflows

**"What's my agenda today?"** — Fetch: todoist tasks (filter: 'today'), exodus upcoming interviews, muse content deadlines, sisyphus today's session, progression activities. Synthesize into a timeline.

**"What's in today's digest?"** — Get latest muse digest and summarize the top AI/ML stories with why-they-matter.

**"Set my agenda"** — Create todoist tasks with `due_datetime` and `duration` (in minutes) to build a calendar-friendly schedule.

**"Update on ongoing"** — Check: active job applications (exodus), in-progress content (muse kanban), active workout (sisyphus), habit streaks at risk (progression).

**"Log my health"** — Use sisyphus_upsert_daily_log for weight/protein/calories/water/sleep.

**"Complete a habit"** — Use progression_complete_activity with the activity ID and value.
