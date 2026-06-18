export interface UserResponse {
  id: string
  username: string
  created_at: string
}

export interface Token {
  access_token: string
  token_type: string
}

export interface LoginRequest {
  username: string
  password: string
}

export interface RegisterRequest {
  username: string
  password: string
}

export interface Movie {
  id: string
  user_id: string
  title: string
  genre: string | null
  rating: number | null
  watched_date: string | null
  notes: string | null
  created_at: string
  updated_at: string
}

export interface MovieCreate {
  title: string
  genre?: string
  rating?: number
  watched_date?: string
  notes?: string
}

export interface MovieUpdate {
  title?: string
  genre?: string
  rating?: number
  watched_date?: string
  notes?: string
}

export interface ListMoviesParams {
  genre?: string
  sort_by?: 'title' | 'watched_date'
  order?: 'asc' | 'desc'
}
