# Module 2 — Dashboard

## Overview

Professional React dashboard with dark theme, responsive layout, sidebar navigation, KPI cards, and auth UI wired to the Module 1 backend.

## Folder Structure (Module 2)

```
frontend/
├── public/
│   └── shield.svg
├── src/
│   ├── components/
│   │   ├── auth/
│   │   │   └── ProtectedRoute.tsx    # Auth guards
│   │   ├── dashboard/
│   │   │   ├── StatCard.tsx          # KPI metric cards
│   │   │   ├── RecentActivity.tsx    # Activity feed
│   │   │   └── SystemStatus.tsx      # Service health panel
│   │   └── layout/
│   │       ├── Sidebar.tsx           # Collapsible sidebar nav
│   │       ├── Navbar.tsx            # Top bar + search + profile
│   │       └── DashboardLayout.tsx     # Main layout shell
│   ├── context/
│   │   ├── AuthContext.tsx           # JWT auth state
│   │   └── ThemeContext.tsx          # Dark/light mode
│   ├── data/
│   │   └── dashboardStats.ts         # Mock KPI data (real data in later modules)
│   ├── pages/
│   │   ├── Dashboard.tsx
│   │   ├── Login.tsx
│   │   └── Register.tsx
│   ├── services/
│   │   └── api.ts                    # API client for auth endpoints
│   ├── types/
│   │   └── index.ts
│   ├── App.tsx
│   ├── main.tsx
│   └── index.css                     # Tailwind + custom utilities
├── index.html
├── package.json
├── tailwind.config.js
├── vite.config.ts
└── tsconfig.json
```

## Dashboard KPI Cards

| Card               | Sample Value | Description                    |
|--------------------|--------------|--------------------------------|
| Total Incidents    | 147          | All detected incidents         |
| Critical Incidents | 8            | Highest severity incidents     |
| Resolved Incidents | 112          | Successfully resolved          |
| Open Tickets       | 23           | Active support tickets         |
| Active Alerts      | 15           | Real-time alert count          |

> KPI data is mock/sample for now. Modules 5, 8, and 9 will connect real backend data.

## Features

- **Dark theme** (default) with light mode toggle
- **Collapsible sidebar** with navigation for all planned modules
- **Top navbar** with search bar, notifications bell, user profile dropdown
- **Responsive layout** — mobile-friendly with slide-out sidebar
- **Login / Register** pages connected to `/api/v1/auth/*`
- **Protected routes** — dashboard requires JWT authentication
- **Animations** — fade-in cards, hover effects, smooth transitions

## Setup Commands

```bash
# Terminal 1 — Backend
cd skyassist-ai/backend
.\venv\Scripts\activate
uvicorn main:app --reload --port 8000

# Terminal 2 — Frontend
cd skyassist-ai/frontend
npm install
npm run dev
```

Open http://localhost:5173

## Auth Flow

```
Login Page → POST /api/v1/auth/login → Store JWT in localStorage
         → GET /api/v1/auth/me → Load user profile → Redirect to Dashboard

Register Page → POST /api/v1/auth/register → Auto-login → Dashboard
```

## Tech Used

| Package           | Purpose                    |
|-------------------|----------------------------|
| React 18          | UI framework               |
| TypeScript        | Type safety                |
| Vite              | Build tool + dev server    |
| TailwindCSS       | Styling                    |
| React Router      | Client-side routing        |
| Lucide React      | Icons                      |

## Next Module

**Module 3 — Log Upload System**: Backend endpoint to upload `.log`, `.txt`, `.csv` files with storage in `logs/`.
