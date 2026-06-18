##Requirements Document: MovieNook Frontend

## Introduction

This document defines the functional requirements for the MovieNook React frontend — a single-page application that allows users to register, log in, and manage their personal movie watch list. The frontend communicates exclusively with the existing FastAPI backend REST API. No backend code is modified.

## Glossary

- **User**: A person with a registered account who manages their private movie list
- **JWT_Token**: JSON Web Token returned by the backend on login; stored in localStorage and sent on every protected request
- **Movie**: A record with title, genre, rating, watched date, and notes owned by the authenticated user
- **ProtectedRoute**: A React Router wrapper that redirects unauthenticated users to `/login`
- **AuthContext**: React context that holds authentication state (token, username) and exposes login/logout helpers
- **Axios Interceptor**: A request interceptor on the shared Axios instance that injects `Authorization: Bearer <token>` on every outgoing request

---

## Requirements

### Requirement 1: User Registration

**User Story:** As a new user, I want to register with a username and password so that I can create an account.

#### Acceptance Criteria

1. WHEN the user navigates to `/register`, THE system SHALL display a form with username and password fields and a Register button.
2. WHEN the user submits the form with a username shorter than 3 or longer than 50 characters, THE system SHALL display an inline error without calling the API.
3. WHEN the user submits the form with a password shorter than 8 characters, THE system SHALL display an inline error without calling the API.
4. WHEN the user submits valid credentials, THE system SHALL call `POST /auth/register` and display a loading state on the button.
5. WHEN registration succeeds (HTTP 201), THE system SHALL navigate to `/login`.
6. WHEN the API returns an error (e.g. username already exists), THE system SHALL display the `detail` message from the response inline.
7. WHEN an authenticated user visits `/register`, THE system SHALL redirect them to `/`.

---

### Requirement 2: User Login

**User Story:** As a registered user, I want to log in with my credentials so that I can access my movie list.

#### Acceptance Criteria

1. WHEN the user navigates to `/login`, THE system SHALL display a form with username and password fields and a Sign In button.
2. WHEN the user submits the form, THE system SHALL call `POST /auth/login` and display a loading state on the button.
3. WHEN login succeeds (HTTP 200), THE system SHALL store the `access_token` in localStorage under key `token` and the username under key `username`.
4. WHEN login succeeds, THE system SHALL navigate to `/`.
5. WHEN the API returns HTTP 401, THE system SHALL display the `detail` message from the response inline.
6. WHEN an authenticated user visits `/login`, THE system SHALL redirect them to `/`.

---

### Requirement 3: JWT Authentication Persistence

**User Story:** As a logged-in user, I want my session to persist across page refreshes so that I do not have to log in every time.

#### Acceptance Criteria

1. WHEN the application loads, THE AuthContext SHALL read `token` and `username` from localStorage and restore the authenticated state.
2. WHEN the Axios instance makes any request, THE interceptor SHALL read the token from localStorage and attach `Authorization: Bearer <token>` to the request headers.
3. WHEN no token exists in localStorage, THE interceptor SHALL send the request without an Authorization header.
4. WHEN the user clicks Logout, THE system SHALL remove `token` and `username` from localStorage, clear auth state, and navigate to `/login`.

---

### Requirement 4: Protected Routes

**User Story:** As the system, I want unauthenticated users to be redirected to login so that private data is not exposed.

#### Acceptance Criteria

1. WHEN an unauthenticated user navigates to `/`, `/movies/new`, `/movies/:id`, or `/movies/:id/edit`, THE system SHALL redirect them to `/login`.
2. WHEN an authenticated user navigates to any protected route, THE system SHALL render the requested page.
3. WHEN an authenticated user navigates to `/login` or `/register`, THE system SHALL redirect them to `/`.

---

### Requirement 5: Dashboard — Movie List

**User Story:** As an authenticated user, I want to see all my movies on the dashboard so that I can browse my collection.

#### Acceptance Criteria

1. WHEN the user navigates to `/`, THE system SHALL call `GET /movies` and display a loading spinner while fetching.
2. WHEN movies are returned, THE system SHALL render each movie as a card showing: title, genre badge (if set), star rating out of 10 (if set), and watched date (if set).
3. WHEN the user has no movies, THE system SHALL display an empty-state message with a link to add a movie.
4. WHEN the API call fails, THE system SHALL display an inline error message.
5. THE dashboard SHALL include an "+ Add Movie" button that navigates to `/movies/new`.

---

### Requirement 6: Dashboard — Filtering

**User Story:** As an authenticated user, I want to filter my movies by genre so that I can find movies of a specific type.

#### Acceptance Criteria

1. THE dashboard SHALL include a genre text input filter field.
2. WHEN the user types a genre and the input changes, THE system SHALL re-fetch `GET /movies?genre=<value>` with the current filter value.
3. WHEN the genre filter is cleared, THE system SHALL re-fetch without the genre parameter.
4. THE genre filter SHALL use case-insensitive matching (handled server-side via ILIKE).

---

### Requirement 7: Dashboard — Sorting

**User Story:** As an authenticated user, I want to sort my movies by title or watched date so that I can organize my list.

#### Acceptance Criteria

1. THE dashboard SHALL include a sort-by selector with options: None, Title, Watched Date.
2. THE dashboard SHALL include an order toggle button switching between Ascending and Descending.
3. WHEN a sort option is selected, THE system SHALL re-fetch `GET /movies?sort_by=<value>&order=<value>`.
4. WHEN sort is set to None, THE system SHALL fetch without `sort_by` or `order` parameters.
5. THE order toggle SHALL be disabled when no sort option is selected.

---

### Requirement 8: Add Movie

**User Story:** As an authenticated user, I want to add a new movie with its details so that I can track what I have watched.

#### Acceptance Criteria

1. WHEN the user navigates to `/movies/new`, THE system SHALL display a form with fields: Title (required), Genre, Rating (1.0–10.0), Watched Date, Notes.
2. WHEN the user submits without a title, THE system SHALL display an inline validation error without calling the API.
3. WHEN the user submits with a rating outside 1.0–10.0, THE system SHALL display an inline validation error.
4. WHEN the user submits valid data, THE system SHALL call `POST /movies` and show a loading state on the submit button.
5. WHEN creation succeeds (HTTP 201), THE system SHALL navigate to `/`.
6. WHEN the API returns an error, THE system SHALL display the `detail` message inline.

---

### Requirement 9: Movie Detail

**User Story:** As an authenticated user, I want to view the full details of a movie so that I can review all the information I stored.

#### Acceptance Criteria

1. WHEN the user navigates to `/movies/:id`, THE system SHALL call `GET /movies/:id` and display a loading spinner.
2. WHEN the movie is returned, THE system SHALL display all fields: title, genre, rating, watched date, notes, date added, last updated.
3. WHEN the API returns HTTP 404, THE system SHALL display a "Movie not found" error message.
4. THE detail page SHALL include an Edit button that navigates to `/movies/:id/edit`.
5. THE detail page SHALL include a Delete button that shows a confirmation dialog before calling `DELETE /movies/:id`.
6. WHEN deletion succeeds (HTTP 204), THE system SHALL navigate to `/`.
7. THE detail page SHALL include a Back button that navigates to `/`.

---

### Requirement 10: Edit Movie

**User Story:** As an authenticated user, I want to update a movie's details so that I can correct or add information over time.

#### Acceptance Criteria

1. WHEN the user navigates to `/movies/:id/edit`, THE system SHALL call `GET /movies/:id` to pre-populate the form.
2. THE edit form SHALL use the same MovieForm component as Add Movie, pre-filled with existing values.
3. WHEN the user submits valid changes, THE system SHALL call `PATCH /movies/:id` with only the changed fields and show a loading state.
4. WHEN the update succeeds (HTTP 200), THE system SHALL navigate to `/movies/:id`.
5. WHEN the API returns an error, THE system SHALL display the `detail` message inline.
6. THE edit page SHALL include a Back button that navigates to `/movies/:id`.

---

### Requirement 11: Delete Movie

**User Story:** As an authenticated user, I want to delete a movie from my list so that I can keep my collection current.

#### Acceptance Criteria

1. Delete can be triggered from either the Dashboard (MovieCard) or the Movie Detail page.
2. WHEN the user clicks Delete, THE system SHALL show a `window.confirm` dialog with the movie title.
3. WHEN the user confirms, THE system SHALL call `DELETE /movies/:id`.
4. WHEN deletion succeeds (HTTP 204), THE system SHALL remove the movie from the displayed list or navigate to `/`.
5. WHEN the API returns an error, THE system SHALL display an inline error message.

---

### Requirement 12: Navigation and Layout

**User Story:** As an authenticated user, I want a consistent navigation bar so that I can move between pages and log out.

#### Acceptance Criteria

1. ALL protected pages SHALL render inside a Layout component containing a top navigation bar.
2. THE navigation bar SHALL display the brand name "MovieNook" on the left as a link to `/`.
3. THE navigation bar SHALL display the logged-in username on the right.
4. THE navigation bar SHALL include a Logout button that clears auth state and redirects to `/login`.

---

### Requirement 13: Loading States

**User Story:** As a user, I want visual feedback during async operations so that I know the app is working.

#### Acceptance Criteria

1. WHEN any API call is in flight, THE system SHALL show a loading indicator (spinner or disabled button with spinner).
2. Submit buttons SHALL be disabled and show a spinner while their form submission is pending.
3. Full-page data fetches SHALL show a centered LoadingSpinner component.

---

### Requirement 14: Error Handling

**User Story:** As a user, I want clear error messages when something goes wrong so that I understand what happened.

#### Acceptance Criteria

1. ALL API errors SHALL display the `detail` field from the response body as an inline message near the relevant UI.
2. WHEN a network error occurs (no response), THE system SHALL display "Unable to connect. Please try again."
3. Error messages SHALL be visible without scrolling whenever possible.
4. Error messages SHALL be cleared when the user retries the operation.
