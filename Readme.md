| Platform            | Command                                                           |
| ------------------- | ----------------------------------------------------------------- |
| Web Development     | `npm run dev`                                                   |
| Desktop Development | `npm run dev` + `npm run electron:dev`                        |
| Cloud Run           | `gcloud run deploy web-app --source .`                          |
| Desktop Installer   | `npm run electron:build:win` → `release/EzeeGenie Setup.exe` |

# Electron Deployment

## To test the desktop app

* Terminal 1: Start Vite dev server
  * npm run dev
* Terminal 2: Start Electron (after Vite is ready)
  * npm run electron:dev

## To build the installer:

* Run this in a windows powershell opened as an administrator.
* npm run electron:build:win # Windows .exe
* The installer will be created in the `release/` folder.

## To Rebuild the Windows Setup File

* Remove-Item -Recurse -Force "release"
* npm run electron:build:win

# Google Cloud Run Deployment

C:\EzeeGenie\web-app> gcloud run deploy web-app --source . --platform managed --region asia-south1 --allow-unauthenticated
App URl: https://web-app-19493053926.asia-south1.run.app/
Build History: https://console.cloud.google.com/cloud-build/builds?project=planar-leaf-481303-m4

Task List
=========

1. Q and A implementation
2. Multi topic handling.
3. Combine topic documents together for a chapter.
4. Material theme conversion

Migration Tool
==============

1. Convert Chapter level word document to json.
2. Updates db/`<standard>`/`<subject>`.json file.
3. Uploads the images to content-images repository.
4. Pushes the files to content-images repository.
5. The input-file should be in the same folder as the script.
6. The input file name should be in the format `<chapter>`.docx
7. Do not include topic numbers in the input file name.

Command Line Usage:
python migration.py `<standard>` `<subject>` `<input-file>`

Example:
cd doc-to-json-converter
python migration.py 6 science 10.docx

Tech Stack Summary
==================

Development
│
├── Frontend: React (Vite)
├── Backend: Node.js (Express)
├── Database: JSON database
├── Storage: Cloudflare R2
│
└── Content Pipeline (Build-time)
    ├── Authoring: Python Tools
    ├── Compilation: Python Publisher Script
    └── Output: content.db + media/ directory

Deployment
│
├── Web App (Cloud, Multi-user)
│   ├── Frontend: React (Vercel)
│   ├── Backend: Supabase Edge Functions (Deno/TS)
│   ├── Database: Supabase Postgres
│   └── Storage: Cloudflare R2
│
└── Desktop App (Local, Single-user)
    ├── Frontend: React (Electron)
    ├── Database: SQLite (pre-packaged)
    └── Storage: Local Filesystem

Recommended Project Structure
=============================

EzeeScore Newton
|
├── Tools/
|   ├── Migration/
|   |   ├── migration.py
|   |   |   ├── 1. Objects Scanner
|   |   |   ├── 2. Concepts Exporter
|   |   |   └── 3. QA Exporter
|   ├── pdf-to-json-converter/
├── supabase/
│   ├── migrations/
│   │   ├── 001_initial_schema.sql
│   │   └── 002_sample_data.sql
│   ├── seed/
│   │   ├── publishers.csv
│   │   └── question_types.json
│   └── functions/
│       └── export-to-sqlite.sql
├── apps/
│   ├── web/           # React + Supabase
│   └── desktop/       # Electron + SQLite
├── packages/
│   ├── database/
│   │   ├── schema/    # Shared TypeScript types
│   │   └── export/    # Python SQLite generator
│   └── shared/        # Common code
└── scripts/
    ├── export-publisher.py
    └── build-desktop.py

Miscellaneous Notes
===================

https://m3.material.io/
npm install @mui/material @emotion/react @emotion/styled

## Create New Project

npm create vite@latest web-app -- --template react
