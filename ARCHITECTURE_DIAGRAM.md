# Sheet Updater - Architecture & Flow

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Flask Application                       │
│                         (app.py)                             │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          │ registers blueprint
                          │
┌─────────────────────────▼───────────────────────────────────┐
│              Sheet Updater Routes                            │
│          (sheet_updater_routes.py)                           │
│                                                              │
│  Routes:                                                     │
│  • GET  /sheet-updater           → Show UI                  │
│  • POST /sheet-updater/start     → Start job                │
│  • GET  /sheet-updater/progress  → Get progress             │
│  • GET/POST /sheet-updater/config → Manage config           │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          │ calls
                          │
┌─────────────────────────▼───────────────────────────────────┐
│            Sheet Updater Handler                             │
│          (sheet_updater_handler.py)                          │
│                                                              │
│  Main Function: run_sheet_updater()                         │
│  • Manages progress tracking                                │
│  • Orchestrates the update flow                             │
│  • Handles errors and logging                               │
└────┬──────────────────┬──────────────────┬──────────────────┘
     │                  │                  │
     │ uses             │ uses             │ uses
     │                  │                  │
┌────▼─────────┐  ┌────▼─────────┐  ┌────▼──────────────┐
│   Mantis     │  │   GitLab     │  │ Sheet Updater     │
│  Operations  │  │  Operations  │  │   Operations      │
│              │  │              │  │                   │
│ • get_ticket │  │ • get_merge  │  │ • get_tickets     │
│   _data()    │  │   _request() │  │ • update_status() │
└──────────────┘  └──────────────┘  └───────────────────┘
```

## Data Flow

```
1. User Input
   ┌──────────────────────────────────────┐
   │  User enters Google Sheet URL        │
   │  in the web interface                │
   └────────────────┬─────────────────────┘
                    │
2. Read Sheet       ▼
   ┌──────────────────────────────────────┐
   │  Read all ticket numbers from        │
   │  Column A (starting row 2)           │
   └────────────────┬─────────────────────┘
                    │
3. Process Each     ▼
   ┌──────────────────────────────────────┐
   │  For each ticket:                    │
   │  ┌────────────────────────────────┐  │
   │  │ Fetch ticket from Mantis       │  │
   │  └────────────┬───────────────────┘  │
   │               │                      │
   │  ┌────────────▼───────────────────┐  │
   │  │ Extract MR URL from notes      │  │
   │  └────────────┬───────────────────┘  │
   │               │                      │
   │  ┌────────────▼───────────────────┐  │
   │  │ Fetch MR from GitLab           │  │
   │  └────────────┬───────────────────┘  │
   │               │                      │
   │  ┌────────────▼───────────────────┐  │
   │  │ Check labels & merge status    │  │
   │  └────────────┬───────────────────┘  │
   │               │                      │
   │  ┌────────────▼───────────────────┐  │
   │  │ Update sheet row               │  │
   │  └────────────────────────────────┘  │
   └──────────────────────────────────────┘
                    │
4. Complete         ▼
   ┌──────────────────────────────────────┐
   │  Log summary and show results        │
   └──────────────────────────────────────┘
```

## MR Label Detection Logic

```
GitLab MR Labels
       │
       ▼
┌─────────────────────────────────────────┐
│  Check if any of these labels exist:    │
│                                         │
│  Code Reviewed?                         │
│  ├─ "Code Reviewed" → YES               │
│  └─ "Reviewed"      → YES               │
│                                         │
│  QA Verified?                           │
│  ├─ "QA Verified"   → YES               │
│  └─ "QA Accepted"   → YES               │
│                                         │
│  Ticket Merged?                         │
│  └─ state == "merged" → YES             │
└─────────────────────────────────────────┘
       │
       ▼
Update Sheet Columns
├─ Code Reviewed = 1 or 0
├─ QA Verified   = 1 or 0
└─ Ticket Merged = 1 or 0
```

## Component Responsibilities

### Sheet Updater Handler
- **Purpose**: Orchestrate the entire update process
- **Responsibilities**:
  - Initialize operations classes
  - Read configuration
  - Loop through tickets
  - Track progress
  - Handle exceptions
  - Log results

### Sheet Updater Operations
- **Purpose**: Interface with Google Sheets API
- **Responsibilities**:
  - Authenticate with Google
  - Read ticket numbers
  - Find column indices dynamically
  - Update cell values
  - Handle sheet errors

### Mantis Operations (Reused)
- **Purpose**: Interface with Mantis API
- **Responsibilities**:
  - Fetch ticket data
  - Get ticket notes
  - Authentication

### GitLab Operations (Reused)
- **Purpose**: Interface with GitLab API
- **Responsibilities**:
  - Fetch merge request data
  - Get labels and state
  - Authentication

## Progress Tracking

```python
progress = {
    "status": "idle" | "running" | "completed" | "error",
    "percentage": 0-100,
    "message": "Human readable status"
}
```

Progress is updated at these points:
- 0%: Idle
- 10%: Reading tickets from sheet
- 10-95%: Processing tickets (proportional)
- 100%: Completed

## Error Handling

```
┌─────────────────────────────────┐
│  Try to process ticket          │
└────────────┬────────────────────┘
             │
    ┌────────▼──────────┐
    │ Ticket exists?    │
    └────┬────────┬─────┘
         │        │
      YES│        │NO
         │        └─────► Log warning, continue
         │
    ┌────▼──────────┐
    │ MR URL found? │
    └────┬────────┬─┘
         │        │
      YES│        │NO
         │        └─────► Set all to 0, continue
         │
    ┌────▼───────────┐
    │ MR data valid? │
    └────┬────────┬──┘
         │        │
      YES│        │NO
         │        └─────► Log error, continue
         │
    ┌────▼──────────────┐
    │ Update sheet      │
    └───────────────────┘
```

## Configuration Flow

```
User Enters Sheet URL
      │
      ▼
Extract Sheet Key via Regex
      │
      ▼
Update config JSON file
      │
      ▼
Save to disk
      │
      ▼
Use in next run
```

## Integration with Existing System

```
Existing Features          New Feature
┌──────────────┐          ┌──────────────┐
│  Regression  │          │    Sheet     │
│    Merge     │          │   Updater    │
└──────┬───────┘          └──────┬───────┘
       │                         │
       └──────────┬──────────────┘
                  │
         ┌────────▼─────────┐
         │  Shared Classes  │
         │                  │
         │ • MantisOps      │
         │ • GitLabOps      │
         │ • ConfigMgr      │
         │ • TokenMgr       │
         │ • Logger         │
         └──────────────────┘
```

All new code is isolated in separate modules while reusing existing infrastructure classes.
