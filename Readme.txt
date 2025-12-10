## Create new project
npm create vite@latest web-app -- --template react
=====================================================================
TECHNICAL STACK SUMMARY

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

====================================================================
RECOMMENDED PROJECT STRUCTURE

EzeeScore Newton
|
├── Tools/
|   ├── Migration/
|   |   ├── migration.py
|   |   |   ├── 1. SmartArt, Drawing, Tables Scanner
|   |   |   └── 2. Word Document to JSON Exporter
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

## Dark Theme Material UI
https://m3.material.io/
npm install @mui/material @emotion/react @emotion/styled

Things to do:
1. Equations handling
2. Equations conversion
3. Q and A implementation
4. Material theme conversion