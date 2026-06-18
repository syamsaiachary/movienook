import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { getMovie, updateMovie } from '../api/movies'
import type { Movie, MovieCreate } from '../types'
import MovieForm from '../components/MovieForm'
import LoadingSpinner from '../components/LoadingSpinner'
import { AxiosError } from 'axios'

export default function EditMoviePage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [movie, setMovie] = useState<Movie | null>(null)
  const [isLoadingMovie, setIsLoadingMovie] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!id) return
    getMovie(id)
      .then(setMovie)
      .catch((err) => {
        if (err instanceof AxiosError && err.response?.status === 404) {
          setError('Movie not found.')
        } else {
          setError('Failed to load movie.')
        }
      })
      .finally(() => setIsLoadingMovie(false))
  }, [id])

  async function handleSubmit(data: MovieCreate) {
    if (!id) return
    setIsSaving(true)
    setError('')
    try {
      await updateMovie(id, data)
      navigate(`/movies/${id}`)
    } catch (err) {
      if (err instanceof AxiosError && err.response) {
        const detail = err.response.data?.detail
        setError(typeof detail === 'string' ? detail : 'Failed to update movie.')
      } else {
        setError('Unable to connect. Please try again.')
      }
    } finally {
      setIsSaving(false)
    }
  }

  if (isLoadingMovie) return <LoadingSpinner />

  if (error && !movie) {
    return (
      <div className="max-w-xl mx-auto">
        <Link to={id ? `/movies/${id}` : '/'} className="text-gray-500 hover:text-gray-700 text-sm">← Back</Link>
        <div className="bg-red-50 border border-red-200 text-red-700 rounded-md px-4 py-3 mt-4 text-sm" role="alert">{error}</div>
      </div>
    )
  }

  if (!movie) return null

  const defaultValues: Partial<MovieCreate> = {
    title: movie.title,
    genre: movie.genre ?? undefined,
    rating: movie.rating ?? undefined,
    watched_date: movie.watched_date ?? undefined,
    notes: movie.notes ?? undefined,
  }

  return (
    <div className="max-w-xl mx-auto">
      <div className="flex items-center gap-3 mb-6">
        <Link to={`/movies/${id}`} className="text-gray-500 hover:text-gray-700 text-sm">← Back</Link>
        <h1 className="text-2xl font-bold text-gray-900">Edit Movie</h1>
      </div>
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 rounded-md px-4 py-3 mb-4 text-sm" role="alert">
          {error}
        </div>
      )}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <MovieForm defaultValues={defaultValues} onSubmit={handleSubmit} isLoading={isSaving} />
      </div>
    </div>
  )
}
