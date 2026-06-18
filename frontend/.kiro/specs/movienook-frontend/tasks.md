# Implementation Tasks: MovieNook Frontend

## Overview

This plan tracks the implementation of the MovieNook React + TypeScript + Vite frontend. All 26 files are already generated and located under `frontend/`. Tasks are marked completed where the file exists and is correct, and left open for any future modifications or additions.

---

## Tasks

### Phase 1 — Project Scaffold

- [x] 1.1 Create `package.json` with pinned dependencies
  - react@18.3.1, react-dom@18.3.1, react-router-dom@6.26.2, axios@1.7.7
  - typescript@5.6.3, vite@5.4.9, @vitejs/plugin-react@4.3.2
  - tailwindcss@3.4.14, postcss@8.4.47, autoprefixer@10.4.20
  - @types/react@18.3.11, @types/react-dom@18.3.1
  - _Requirements: —_

- [x] 1.2 Create `vite.config.ts`
  - Plugin: `@vitejs/plugin-react`
  - Dev server port: 5173
  - _Requirements: —_

- [x] 1.3 Create `tsconfig.json` and `tsconfig.node.json`
  - strict mode, ES2020 target, react-jsx
  - _Requirements: —_

- [x] 1.4 Create `tailwind.config.js` and `postcss.config.js`
  - Content paths covering `./index.html` and `./src/**/*.{ts,tsx}`
  - _Requirements: —_

- [x] 1.5 Create `index.html`
  - Root div `#root`, script pointing to `src/main.tsx`, title "MovieNook"
  - _Requirements: —_

---

### Phase 2 — Types and API Layer

- [x] 2.1 Create `src/types/index.ts`
  - Interfaces: `UserResponse`, `Token`, `LoginRequest`, `RegisterRequest`
  - Interfaces: `Movie`, `MovieCreate`, `MovieUpdate`, `ListMoviesParams`
  - _Requirements: 2, 3, 5, 6, 7, 8, 9, 10_

- [x] 2.2 Create `src/api/axios.ts`
  - Single Axios instance with `baseURL: 'http://localhost:8000'`
  - Request interceptor reads `localStorage.getItem('token')` and sets `Authorization: Bearer <token>`
  - _Requirements: 3.2, 3.3_

- [x] 2.3 Create `src/api/auth.ts`
  - `register(data: RegisterRequest): Promise<UserResponse>`
  - `login(data: LoginRequest): Promise<Token>`
  - _Requirements: 1, 2_

- [x] 2.4 Create `src/api/movies.ts`
  - `listMovies(params?: ListMoviesParams): Promise<Movie[]>`
  - `getMovie(id: string): Promise<Movie>`
  - `createMovie(data: MovieCreate): Promise<Movie>`
  - `updateMovie(id: string, data: MovieUpdate): Promise<Movie>`
  - `deleteMovie(id: string): Promise<void>`
  - _Requirements: 5, 6, 7, 8, 9, 10, 11_

---

### Phase 3 — Auth Context

- [x] 3.1 Create `src/context/AuthContext.tsx`
  - State: `token`, `username` — initialized from localStorage on mount
  - Exposes: `isAuthenticated`, `user: { username }`, `login()`, `logout()`
  - `login()`: writes `token` and `username` to localStorage + updates state
  - `logout()`: removes `token` and `username` from localStorage + clears state
  - _Requirements: 2.3, 3.1, 3.4_

---

### Phase 4 — Shared Components

- [x] 4.1 Create `src/components/LoadingSpinner.tsx`
  - Centered animated CSS spinner
  - Used for full-page loading states
  - _Requirements: 13.3_

- [x] 4.2 Create `src/components/ProtectedRoute.tsx`
  - Renders `<Outlet />` if `isAuthenticated`, otherwise `<Navigate to="/login" replace />`
  - _Requirements: 4.1, 4.2_

- [x] 4.3 Create `src/components/Layout.tsx`
  - Top navbar: "MovieNook" brand (left, links to `/`), username + Logout button (right)
  - Logout calls `auth.logout()` then `navigate('/login')`
  - Wraps `<Outlet />` in a max-width container
  - _Requirements: 12.1, 12.2, 12.3, 12.4_

- [x] 4.4 Create `src/components/MovieCard.tsx`
  - Props: `movie: Movie`, `onDelete: (id: string) => void`
  - Displays: title (link to `/movies/:id`), genre badge, star rating (10 stars), watched date
  - Delete button: `window.confirm` → `onDelete(movie.id)`
  - _Requirements: 5.2, 11.2, 11.3_

- [x] 4.5 Create `src/components/MovieForm.tsx`
  - Props: `defaultValues?: Partial<MovieCreate>`, `onSubmit`, `isLoading`
  - Fields: title (required), genre, rating (1–10 step 0.1), watched_date (date), notes (textarea)
  - Client-side validation on submit; per-field inline error messages
  - Submit button disabled + spinner when `isLoading` is true
  - _Requirements: 8.1, 8.2, 8.3, 10.2, 13.1, 13.2_

---

### Phase 5 — Pages

- [x] 5.1 Create `src/pages/LoginPage.tsx`
  - Fields: username, password; Sign In button
  - On success: store token + username via `AuthContext.login()`, navigate to `/`
  - On error: display `detail` inline
  - Redirect to `/` if already authenticated
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6_

- [x] 5.2 Create `src/pages/RegisterPage.tsx`
  - Fields: username, password; Register button
  - Client-side validation (username 3–50, password min 8) before API call
  - On success: navigate to `/login`
  - On error: display `detail` inline
  - Redirect to `/` if already authenticated
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7_

- [x] 5.3 Create `src/pages/DashboardPage.tsx`
  - Fetches `GET /movies` with current filter/sort state
  - Filter: genre text input
  - Sort: sort-by select (None / Title / Watched Date) + asc/desc toggle
  - Renders `MovieCard` grid; empty-state message when no movies
  - `handleDelete(id)` → `deleteMovie(id)` → remove from local state
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 6.1, 6.2, 6.3, 7.1, 7.2, 7.3, 7.4, 7.5, 11.4_

- [x] 5.4 Create `src/pages/AddMoviePage.tsx`
  - Renders `<MovieForm>` with no defaults
  - On submit: `createMovie(data)` → navigate to `/`
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6_

- [x] 5.5 Create `src/pages/MovieDetailPage.tsx`
  - Fetches `GET /movies/:id` on mount
  - Displays all fields in a definition list
  - Edit button → `/movies/:id/edit`; Back button → `/`
  - Delete button → `window.confirm` → `deleteMovie(id)` → navigate to `/`
  - 404 response → display error message
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7, 11.1, 11.2, 11.3, 11.4_

- [x] 5.6 Create `src/pages/EditMoviePage.tsx`
  - Fetches `GET /movies/:id` to pre-populate `<MovieForm>`
  - On submit: `updateMovie(id, data)` → navigate to `/movies/:id`
  - Back button → `/movies/:id`
  - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6_

---

### Phase 6 — App Entry

- [x] 6.1 Create `src/index.css`
  - Tailwind directives: `@tailwind base`, `@tailwind components`, `@tailwind utilities`
  - _Requirements: —_

- [x] 6.2 Create `src/App.tsx`
  - Route definitions with `PublicOnly` and `ProtectedRoute` guards
  - Catch-all `*` redirects to `/`
  - _Requirements: 3.4, 4.1, 4.2, 4.3_

- [x] 6.3 Create `src/main.tsx`
  - Wraps `<App>` in `<StrictMode>`, `<BrowserRouter>`, `<AuthProvider>`
  - _Requirements: —_

---

## Future Tasks (not yet implemented)

- [ ] F1. Add toast notifications for success actions (movie created, updated, deleted)
- [ ] F2. Add pagination or infinite scroll to the dashboard when movie count grows large
- [ ] F3. Add a profile page showing account details (username, created date)
- [ ] F4. Add keyboard accessibility improvements (focus trapping in modals, skip links)
- [ ] F5. Add optimistic UI updates on delete to avoid re-fetch latency

---

## Task Dependency Graph

```
Phase 1 (Scaffold)
    └── Phase 2 (Types + API)
            └── Phase 3 (AuthContext)
                    └── Phase 4 (Components)
                            └── Phase 5 (Pages)
                                    └── Phase 6 (Entry)
```

Each phase depends on all previous phases being complete before it can be built and tested end-to-end.
