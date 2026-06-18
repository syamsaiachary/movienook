# Design Document: MovieNook Frontend

## Overview

The MovieNook frontend is a React 18 single-page application built with TypeScript and Vite. It communicates exclusively with the existing FastAPI backend at `http://localhost:8000`. Authentication is stateless — JWT tokens are stored in localStorage and injected on every request via an Axios interceptor. Routing is handled by React Router v6 with protected and public-only route guards. Styling uses Tailwind CSS throughout with no custom CSS beyond the Tailwind directives.

---

## Architecture

### High-Level Component Tree

```
BrowserRouter
└── AuthProvider
    └── App
        ├── /login         → LoginPage         (public only)
        ├── /register      → RegisterPage      (public only)
        └── ProtectedRoute
            └── Layout (navbar)
                ├── /                  → DashboardPage
                ├── /movies/new        → AddMoviePage
                ├── /movies/:id        → MovieDetailPage
                └── /movies/:id/edit   → EditMoviePage
```

### Data Flow

```
User Action
    │
    ▼
Page / Component (local state: data, isLoading, error)
    │
    ▼
API module (src/api/*.ts)
    │
    ▼
Axios instance (src/api/axios.ts)
    │  ← interceptor reads localStorage token → adds Authorization header
    ▼
FastAPI Backend (http://localhost:8000)
    │
    ▼
Response → update local state → re-render
```

All state is local to each page component. There is no global state beyond authentication (AuthContext). No Redux, Zustand, or query libraries are used.

---

## Layers and Responsibilities

### 1. Entry Point (`src/main.tsx`)
- Wraps the app in `<BrowserRouter>`, `<AuthProvider>`, and `<StrictMode>`
- Mounts to `#root`

### 2. App Router (`src/App.tsx`)
- Defines all routes using React Router v6 `<Routes>` / `<Route>`
- `PublicOnly` wrapper: redirects authenticated users away from `/login` and `/register` to `/`
- `ProtectedRoute` wrapper: redirects unauthenticated users to `/login`
- Catch-all `*` route redirects to `/`

### 3. Auth Context (`src/context/AuthContext.tsx`)
- Holds `token` and `username` in React state, initialized from localStorage
- Exposes: `isAuthenticated: boolean`, `user: { username: string } | null`, `login(token, username)`, `logout()`
- `login()`: writes to localStorage + updates state
- `logout()`: removes from localStorage + clears state
- Does **not** make any API calls

### 4. Axios Instance (`src/api/axios.ts`)
- Single instance with `baseURL: 'http://localhost:8000'`
- Request interceptor reads `localStorage.getItem('token')` per-request and sets `Authorization: Bearer <token>` if present
- All API modules import this instance — no secondary instances anywhere

### 5. API Modules
- `src/api/auth.ts`: `register(data)`, `login(data)` — return typed response objects
- `src/api/movies.ts`: `listMovies(params?)`, `getMovie(id)`, `createMovie(data)`, `updateMovie(id, data)`, `deleteMovie(id)`
- All functions are `async` and return typed promises. They do not catch errors — errors propagate to the calling component.

### 6. Shared Components
- `LoadingSpinner`: Centered animated spinner for full-page loading states
- `ProtectedRoute`: Renders `<Outlet />` if authenticated, otherwise `<Navigate to="/login" />`
- `Layout`: Top navbar (brand + username + logout) wrapping `<Outlet />`
- `MovieCard`: Displays a single movie in the dashboard grid; handles inline delete
- `MovieForm`: Reusable controlled form for Add and Edit pages; accepts `defaultValues`, `onSubmit`, `isLoading`

### 7. Pages
Each page owns its own `isLoading`, `error`, and data state. Pages call API modules directly.

---

## Component Specifications

### `AuthContext`

```ts
interface AuthContextValue {
  isAuthenticated: boolean
  user: { username: string } | null
  login: (token: string, username: string) => void
  logout: () => void
}
```

State initialized from localStorage on mount so sessions survive page refresh.

---

### `ProtectedRoute`

```tsx
// Redirects to /login if not authenticated, otherwise renders child routes
export default function ProtectedRoute() {
  const { isAuthenticated } = useAuth()
  return isAuthenticated ? <Outlet /> : <Navigate to="/login" replace />
}
```

---

### `Layout`

- Fixed top navbar with indigo background
- Left: "MovieNook" brand linked to `/`
- Right: username (muted) + Logout button
- Main content area: max-width container, vertical padding, renders `<Outlet />`

---

### `MovieForm`

Props:
```ts
interface MovieFormProps {
  defaultValues?: Partial<MovieCreate>
  onSubmit: (data: MovieCreate) => void
  isLoading: boolean
}
```

Fields:
| Field        | Input Type | Validation                        |
|--------------|------------|-----------------------------------|
| title        | text       | Required, max 200 chars           |
| genre        | text       | Optional, max 100 chars           |
| rating       | number     | Optional, 1.0–10.0, step 0.1     |
| watched_date | date       | Optional, YYYY-MM-DD              |
| notes        | textarea   | Optional, max 1000 chars          |

- Client-side validation runs on submit before any API call
- Each field shows its own inline error message
- Submit button is disabled and shows spinner while `isLoading` is true

---

### `MovieCard`

Props:
```ts
interface MovieCardProps {
  movie: Movie
  onDelete: (id: string) => void
}
```

Layout:
- Title (bold, links to `/movies/:id`)
- Genre badge (indigo pill, only if set)
- Star rating (10 filled/unfilled stars + numeric value, only if set)
- Watched date (only if set)
- Delete button at card bottom — calls `window.confirm` then `onDelete(movie.id)`

---

## Page Specifications

### `LoginPage` (`/login`)

State: `username`, `password`, `isLoading`, `error`

Flow:
1. Submit → set `isLoading = true`, clear `error`
2. Call `login({ username, password })`
3. On success: call `auth.login(token, username)` → navigate to `/`
4. On error: set `error` from `err.response.data.detail` or network fallback message

---

### `RegisterPage` (`/register`)

State: `username`, `password`, `isLoading`, `error`

Flow:
1. Client-side validation (username 3–50, password min 8) before API call
2. Submit → call `register({ username, password })`
3. On success (201): navigate to `/login`
4. On error: display `detail` from response

---

### `DashboardPage` (`/`)

State: `movies`, `isLoading`, `error`, `genreFilter`, `sortBy`, `order`

Flow:
1. `useEffect` + `useCallback` — re-fetches on every change to `genreFilter`, `sortBy`, `order`
2. Builds `ListMoviesParams` from current state — omits empty/default values
3. Renders filter bar (genre input, sort-by select, asc/desc toggle)
4. Renders grid of `MovieCard` components
5. `handleDelete(id)` calls `deleteMovie(id)` then filters movie out of local state

Query param logic:
- `genre` only sent if non-empty after trim
- `sort_by` + `order` only sent if `sortBy !== ''`

---

### `AddMoviePage` (`/movies/new`)

State: `isLoading`, `error`

Renders `<MovieForm>` with no `defaultValues`.

Flow:
1. `handleSubmit(data)` → call `createMovie(data)`
2. On success: navigate to `/`
3. On error: display `detail`

---

### `MovieDetailPage` (`/movies/:id`)

State: `movie`, `isLoading`, `isDeleting`, `error`

Flow:
1. `useEffect` on `id` → call `getMovie(id)`
2. Render all fields in a definition list
3. Edit button → `/movies/:id/edit`
4. Delete button → `window.confirm` → `deleteMovie(id)` → navigate to `/`
5. 404 from API → display "Movie not found"

---

### `EditMoviePage` (`/movies/:id/edit`)

State: `movie`, `isLoadingMovie`, `isSaving`, `error`

Flow:
1. `useEffect` on `id` → call `getMovie(id)` to populate form defaults
2. Render `<MovieForm defaultValues={...}>` once movie is loaded
3. `handleSubmit(data)` → call `updateMovie(id, data)`
4. On success: navigate to `/movies/:id`
5. On error: display `detail`

---

## Type Definitions (`src/types/index.ts`)

```ts
// Auth
interface UserResponse { id: string; username: string; created_at: string }
interface Token { access_token: string; token_type: string }
interface LoginRequest { username: string; password: string }
interface RegisterRequest { username: string; password: string }

// Movies
interface Movie {
  id: string; user_id: string; title: string
  genre: string | null; rating: number | null
  watched_date: string | null; notes: string | null
  created_at: string; updated_at: string
}
interface MovieCreate {
  title: string; genre?: string; rating?: number
  watched_date?: string; notes?: string
}
interface MovieUpdate {
  title?: string; genre?: string; rating?: number
  watched_date?: string; notes?: string
}
interface ListMoviesParams {
  genre?: string
  sort_by?: 'title' | 'watched_date'
  order?: 'asc' | 'desc'
}
```

---

## Error Handling Strategy

All API calls follow this pattern in page components:

```ts
try {
  setIsLoading(true)
  setError('')
  const data = await apiCall(...)
  // handle success
} catch (err) {
  if (err instanceof AxiosError && err.response) {
    const detail = err.response.data?.detail
    setError(typeof detail === 'string' ? detail : 'An error occurred.')
  } else {
    setError('Unable to connect. Please try again.')
  }
} finally {
  setIsLoading(false)
}
```

Error messages are rendered in a red alert box (`role="alert"`) directly above or below the relevant UI element.

---

## Routing Guards Detail

```tsx
// Public-only: redirect authenticated users away from /login and /register
function PublicOnly({ children }) {
  const { isAuthenticated } = useAuth()
  return isAuthenticated ? <Navigate to="/" replace /> : <>{children}</>
}

// Protected: redirect unauthenticated users to /login
function ProtectedRoute() {
  const { isAuthenticated } = useAuth()
  return isAuthenticated ? <Outlet /> : <Navigate to="/login" replace />
}
```

---

## Build and Dev Configuration

### Vite (`vite.config.ts`)
- Plugin: `@vitejs/plugin-react`
- Dev server port: `5173`
- No proxy configured — frontend calls backend directly at `http://localhost:8000`

### TypeScript (`tsconfig.json`)
- Target: `ES2020`
- `strict: true`
- `jsx: react-jsx`
- Paths: default, no aliases

### Tailwind (`tailwind.config.js`)
- Content: `['./index.html', './src/**/*.{ts,tsx}']`
- No custom theme extensions — uses Tailwind defaults
- Color palette: indigo for primary actions, red for destructive, gray for neutral

---

## Backend API Reference

All endpoints relative to `http://localhost:8000`.

| Method | Path                 | Auth | Request Body / Query                          | Response          |
|--------|----------------------|------|-----------------------------------------------|-------------------|
| POST   | /auth/register       | No   | `{ username, password }`                      | UserResponse 201  |
| POST   | /auth/login          | No   | `{ username, password }`                      | Token 200         |
| GET    | /movies              | Yes  | `?genre&sort_by=title\|watched_date&order=asc\|desc` | Movie[] 200 |
| POST   | /movies              | Yes  | MovieCreate                                   | Movie 201         |
| GET    | /movies/:id          | Yes  | —                                             | Movie 200         |
| PATCH  | /movies/:id          | Yes  | MovieUpdate (partial)                         | Movie 200         |
| DELETE | /movies/:id          | Yes  | —                                             | 204               |

All error responses have shape: `{ detail: string }`
