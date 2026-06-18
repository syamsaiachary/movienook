---
title: MovieNook Frontend
inclusion: always
---

# Project Overview

A React + TypeScript single-page application for the MovieNook personal movie tracking app.
The frontend communicates exclusively with the existing FastAPI backend at `http://localhost:8000`.
No backend code is modified — the frontend is a pure client consuming the REST API.

# Tech Stack

- Package Manager: npm
- Language: TypeScript (strict mode)
- Framework: React 18
- Build Tool: Vite 5
- Routing: React Router v6
- HTTP Client: Axios (with request interceptor for JWT)
- Styling: Tailwind CSS v3
- State: React Context API (AuthContext for auth state)
- Token Storage: localStorage (keys: `token`, `username`)

# Project Structure

```
frontend/
├── index.html
├── package.json
├── vite.config.ts
├── tsconfig.json
├── tsconfig.node.json
├── tailwind.config.js
├── postcss.config.js
└── src/
    ├── main.tsx              # Entry point — BrowserRouter + AuthProvider + App
    ├── App.tsx               # Route definitions with guards
    ├── index.css             # Tailwind directives
    ├── types/
    │   └── index.ts          # All shared TypeScript interfaces
    ├── api/
    │   ├── axios.ts          # Axios instance + Bearer token interceptor
    │   ├── auth.ts           # register(), login()
    │   └── movies.ts         # listMovies(), getMovie(), createMovie(), updateMovie(), deleteMovie()
    ├── context/
    │   └── AuthContext.tsx   # isAuthenticated, user, login(), logout()
    ├── components/
    │   ├── ProtectedRoute.tsx
    │   ├── Layout.tsx
    │   ├── MovieCard.tsx
    │   ├── MovieForm.tsx
    │   └── LoadingSpinner.tsx
    └── pages/
        ├── LoginPage.tsx
        ├── RegisterPage.tsx
        ├── DashboardPage.tsx
        ├── AddMoviePage.tsx
        ├── MovieDetailPage.tsx
        └── EditMoviePage.tsx
```

# Backend API Base URL

`http://localhost:8000`

All requests go through `src/api/axios.ts`. Never call `fetch()` or create a second Axios instance.

# Route Map

| Path              | Page              | Auth Required |
|-------------------|-------------------|---------------|
| /login            | LoginPage         | No (redirect to / if logged in) |
| /register         | RegisterPage      | No (redirect to / if logged in) |
| /                 | DashboardPage     | Yes |
| /movies/new       | AddMoviePage      | Yes |
| /movies/:id       | MovieDetailPage   | Yes |
| /movies/:id/edit  | EditMoviePage     | Yes |

# Conventions

- All files: TypeScript (.tsx for JSX, .ts for pure logic)
- All identifiers: camelCase; components: PascalCase
- Error responses from the API always have shape `{ detail: string }` — display `error.response.data.detail`
- Never hardcode the API base URL outside of `src/api/axios.ts`
- Never read localStorage directly outside of `src/context/AuthContext.tsx` and `src/api/axios.ts`
- All async operations must have a loading state and inline error display — no silent failures
- Tailwind only — no custom CSS files beyond `index.css` Tailwind directives
- No test files, no Storybook, no mock data files

# Security Rules

- JWT token stored in localStorage under key `token`
- Axios interceptor reads token per-request — never cache it in module scope
- Unauthenticated users hitting protected routes are redirected to `/login`
- Authenticated users hitting `/login` or `/register` are redirected to `/`
- Token is cleared from localStorage on logout

# Out of Scope

- Any modification to backend files
- Unit or integration tests
- Storybook or documentation files
- Social features, admin panels, password reset
