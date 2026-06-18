import apiClient from './axios'
import type { Movie, MovieCreate, MovieUpdate, ListMoviesParams } from '../types'

export async function listMovies(params?: ListMoviesParams): Promise<Movie[]> {
  const response = await apiClient.get<Movie[]>('/movies', { params })
  return response.data
}

export async function getMovie(id: string): Promise<Movie> {
  const response = await apiClient.get<Movie>(`/movies/${id}`)
  return response.data
}

export async function createMovie(data: MovieCreate): Promise<Movie> {
  const response = await apiClient.post<Movie>('/movies', data)
  return response.data
}

export async function updateMovie(id: string, data: MovieUpdate): Promise<Movie> {
  const response = await apiClient.patch<Movie>(`/movies/${id}`, data)
  return response.data
}

export async function deleteMovie(id: string): Promise<void> {
  await apiClient.delete(`/movies/${id}`)
}
