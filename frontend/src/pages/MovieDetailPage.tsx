import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { getMovie, deleteMovie } from '../api/movies'
import type { Movie } from '../types'
import LoadingSpinner from '../components/LoadingSpinner'
import ConfirmModal from '../components/ConfirmModal'
import { AxiosError } from 'axios'

function DetailRow({ label, value }: { label: string; value: string | number | null }) {
  if (value === null || value === undefined) return null
  return (
    <div className="py-3 border-b border-gray-100 last:border-0">
      <dt className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-0.5">{label}</dt>
      <dd className="text-gray-900 text-sm">{String(value)}</dd>
    </div>
  )
}

export default function MovieDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [movie, setMovie] = useState<Movie | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [isDeleting, setIsDeleting] = useState(false)

  useEffect(() => {
    if (!id) return
    setIsLoading(true)
    getMovie(id)
      .then(setMovie)
      .catch((err) => {
        if (err instanceof AxiosError && err.response?.status === 404) {
          setError('Movie not found.')
        } else {
          setError('Failed to load movie.')
        }
      })
      .finally(() => setIsLoading(false))
  }, [id])

  async function handleDeleteConfirm() {
    if (!movie) return
    setIsDeleting(true)
    try {
      await deleteMovie(movie.id)
      navigate('/')
    } catch {
      setError('Failed to delete movie.')
      setIsDeleting(false)
      setShowModal(false)
    }
  }

  if (isLoading) return <LoadingSpinner />

  if (error && !movie) {
    return (
      <div className="max-w-xl mx-auto">
        <Link to="/" className="text-gray-500 hover:text-gray-700 text-sm">← Back</Link>
        <div className="bg-red-50 border border-red-200 text-red-700 rounded-md px-4 py-3 mt-4 text-sm" role="alert">{error}</div>
      </div>
    )
  }

  if (!movie) return null

  return (
    <>
      <div className="max-w-xl mx-auto">
        <div className="flex items-center gap-3 mb-6">
          <Link to="/" className="text-gray-500 hover:text-gray-700 text-sm">← Back</Link>
          <h1 className="text-2xl font-bold text-gray-900 flex-1 truncate">{movie.title}</h1>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 rounded-md px-4 py-3 mb-4 text-sm" role="alert">
            {error}
          </div>
        )}

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-4">
          <dl>
            <DetailRow label="Title" value={movie.title} />
            <DetailRow label="Genre" value={movie.genre} />
            <DetailRow label="Rating" value={movie.rating !== null ? `${movie.rating} / 10` : null} />
            <DetailRow label="Watched Date" value={movie.watched_date} />
            <DetailRow label="Notes" value={movie.notes} />
            <DetailRow label="Added" value={new Date(movie.created_at).toLocaleDateString()} />
            <DetailRow label="Updated" value={new Date(movie.updated_at).toLocaleDateString()} />
          </dl>
        </div>

        <div className="flex gap-3">
          <Link
            to={`/movies/${movie.id}/edit`}
            className="flex-1 text-center bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2 rounded-md transition-colors text-sm"
          >
            Edit
          </Link>
          <button
            onClick={() => setShowModal(true)}
            className="flex-1 bg-red-600 hover:bg-red-700 text-white font-medium py-2 rounded-md transition-colors text-sm flex items-center justify-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2} aria-hidden="true">
              <path strokeLinecap="round" strokeLinejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
            Delete
          </button>
        </div>
      </div>

      <ConfirmModal
        isOpen={showModal}
        title="Delete Movie"
        message={`Are you sure you want to delete "${movie.title}"? This action cannot be undone.`}
        confirmLabel="Delete"
        isLoading={isDeleting}
        onConfirm={handleDeleteConfirm}
        onCancel={() => setShowModal(false)}
      />
    </>
  )
}
