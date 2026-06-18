import { useState } from 'react'
import { Link } from 'react-router-dom'
import type { Movie } from '../types'
import ConfirmModal from './ConfirmModal'

interface MovieCardProps {
  movie: Movie
  onDelete: (id: string) => Promise<void> | void
}

function StarRating({ rating }: { rating: number }) {
  const filled = Math.round(rating)
  return (
    <span className="flex items-center gap-0.5" aria-label={`Rating: ${rating} out of 10`}>
      {Array.from({ length: 10 }, (_, i) => (
        <svg
          key={i}
          className={`w-3 h-3 ${i < filled ? 'text-yellow-400' : 'text-gray-300'}`}
          fill="currentColor"
          viewBox="0 0 20 20"
          aria-hidden="true"
        >
          <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
        </svg>
      ))}
      <span className="ml-1 text-xs text-gray-600">{rating.toFixed(1)}</span>
    </span>
  )
}

export default function MovieCard({ movie, onDelete }: MovieCardProps) {
  const [showModal, setShowModal] = useState(false)
  const [isDeleting, setIsDeleting] = useState(false)

  async function handleConfirm() {
    setIsDeleting(true)
    await onDelete(movie.id)
    setIsDeleting(false)
    setShowModal(false)
  }

  return (
    <>
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 hover:shadow-md transition-shadow flex flex-col">
        <Link to={`/movies/${movie.id}`} className="flex-1 p-5 block">
          <h3 className="text-gray-900 font-semibold text-lg leading-snug mb-2 line-clamp-2">
            {movie.title}
          </h3>
          {movie.genre && (
            <span className="inline-block bg-indigo-100 text-indigo-700 text-xs font-medium px-2.5 py-0.5 rounded-full mb-2">
              {movie.genre}
            </span>
          )}
          {movie.rating !== null && (
            <div className="mb-2">
              <StarRating rating={movie.rating} />
            </div>
          )}
          {movie.watched_date && (
            <p className="text-gray-500 text-xs">
              Watched: {movie.watched_date}
            </p>
          )}
        </Link>

        <div className="px-5 pb-4">
          <button
            onClick={(e) => { e.preventDefault(); setShowModal(true) }}
            className="w-full text-sm text-red-600 hover:text-white hover:bg-red-600 border border-red-200 rounded-lg py-2 transition-colors font-medium flex items-center justify-center gap-1.5"
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
        onConfirm={handleConfirm}
        onCancel={() => setShowModal(false)}
      />
    </>
  )
}
