import { useState, useEffect, useCallback } from 'react'
import { Link } from 'react-router-dom'
import { listMovies, deleteMovie } from '../api/movies'
import type { Movie, ListMoviesParams } from '../types'
import MovieCard from '../components/MovieCard'
import LoadingSpinner from '../components/LoadingSpinner'
import { AxiosError } from 'axios'

type SortBy = '' | 'title' | 'watched_date'
type Order = 'asc' | 'desc'

export default function DashboardPage() {
  const [movies, setMovies] = useState<Movie[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [genreFilter, setGenreFilter] = useState('')
  const [sortBy, setSortBy] = useState<SortBy>('')
  const [order, setOrder] = useState<Order>('asc')

  const fetchMovies = useCallback(async () => {
    setIsLoading(true)
    setError('')
    try {
      const params: ListMoviesParams = {}
      if (genreFilter.trim()) params.genre = genreFilter.trim()
      if (sortBy) {
        params.sort_by = sortBy
        params.order = order
      }
      const data = await listMovies(params)
      setMovies(data)
    } catch (err) {
      if (err instanceof AxiosError && err.response) {
        setError('Failed to load movies.')
      } else {
        setError('Unable to connect. Please try again.')
      }
    } finally {
      setIsLoading(false)
    }
  }, [genreFilter, sortBy, order])

  useEffect(() => {
    fetchMovies()
  }, [fetchMovies])

  async function handleDelete(id: string) {
    try {
      await deleteMovie(id)
      setMovies((prev) => prev.filter((m) => m.id !== id))
    } catch {
      setError('Failed to delete movie.')
    }
  }

  const inputClass = 'rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent'

  return (
    <div>
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <h1 className="text-2xl font-bold text-gray-900">My Movies</h1>
        <Link
          to="/movies/new"
          className="bg-indigo-600 hover:bg-indigo-700 text-white font-medium px-4 py-2 rounded-md transition-colors text-sm"
        >
          + Add Movie
        </Link>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 p-4 mb-6 flex flex-col sm:flex-row gap-3 flex-wrap">
        <input
          type="text"
          placeholder="Filter by genre..."
          className={`${inputClass} flex-1 min-w-[160px]`}
          value={genreFilter}
          onChange={(e) => setGenreFilter(e.target.value)}
          aria-label="Filter by genre"
        />
        <select
          className={inputClass}
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value as SortBy)}
          aria-label="Sort by"
        >
          <option value="">No sort</option>
          <option value="title">Title</option>
          <option value="watched_date">Watched Date</option>
        </select>
        <button
          className={`${inputClass} flex items-center gap-1 cursor-pointer`}
          onClick={() => setOrder((o) => (o === 'asc' ? 'desc' : 'asc'))}
          disabled={!sortBy}
          aria-label={`Order: ${order === 'asc' ? 'Ascending' : 'Descending'}`}
        >
          {order === 'asc' ? '↑ Asc' : '↓ Desc'}
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 rounded-md px-4 py-3 mb-4 text-sm" role="alert">
          {error}
        </div>
      )}

      {isLoading ? (
        <LoadingSpinner />
      ) : movies.length === 0 ? (
        <div className="text-center py-20 text-gray-400">
          <p className="text-lg mb-2">No movies yet.</p>
          <Link to="/movies/new" className="text-indigo-600 hover:underline text-sm">
            Add your first movie
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {movies.map((movie) => (
            <MovieCard key={movie.id} movie={movie} onDelete={handleDelete} />
          ))}
        </div>
      )}
    </div>
  )
}
