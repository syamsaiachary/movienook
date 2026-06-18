import { useState } from 'react'
import type { MovieCreate } from '../types'

interface MovieFormProps {
  defaultValues?: Partial<MovieCreate>
  onSubmit: (data: MovieCreate) => void
  isLoading: boolean
}

export default function MovieForm({ defaultValues = {}, onSubmit, isLoading }: MovieFormProps) {
  const [title, setTitle] = useState(defaultValues.title ?? '')
  const [genre, setGenre] = useState(defaultValues.genre ?? '')
  const [rating, setRating] = useState(
    defaultValues.rating !== undefined ? String(defaultValues.rating) : ''
  )
  const [watchedDate, setWatchedDate] = useState(defaultValues.watched_date ?? '')
  const [notes, setNotes] = useState(defaultValues.notes ?? '')
  const [errors, setErrors] = useState<Record<string, string>>({})

  function validate(): boolean {
    const errs: Record<string, string> = {}
    if (!title.trim()) errs.title = 'Title is required.'
    if (title.length > 200) errs.title = 'Title must be 200 characters or fewer.'
    if (genre.length > 100) errs.genre = 'Genre must be 100 characters or fewer.'
    if (rating !== '') {
      const r = parseFloat(rating)
      if (isNaN(r) || r < 1 || r > 10) errs.rating = 'Rating must be between 1.0 and 10.0.'
    }
    if (watchedDate && !/^\d{4}-\d{2}-\d{2}$/.test(watchedDate)) {
      errs.watched_date = 'Date must be in YYYY-MM-DD format.'
    }
    if (notes.length > 1000) errs.notes = 'Notes must be 1000 characters or fewer.'
    setErrors(errs)
    return Object.keys(errs).length === 0
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!validate()) return
    const data: MovieCreate = { title: title.trim() }
    if (genre.trim()) data.genre = genre.trim()
    if (rating !== '') data.rating = parseFloat(rating)
    if (watchedDate) data.watched_date = watchedDate
    if (notes.trim()) data.notes = notes.trim()
    onSubmit(data)
  }

  const inputClass = 'w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent'
  const labelClass = 'block text-sm font-medium text-gray-700 mb-1'
  const errorClass = 'text-red-600 text-xs mt-1'

  return (
    <form onSubmit={handleSubmit} noValidate className="space-y-5">
      <div>
        <label className={labelClass} htmlFor="title">Title <span className="text-red-500">*</span></label>
        <input
          id="title"
          type="text"
          className={inputClass}
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          maxLength={200}
          required
        />
        {errors.title && <p className={errorClass}>{errors.title}</p>}
      </div>
      <div>
        <label className={labelClass} htmlFor="genre">Genre</label>
        <input
          id="genre"
          type="text"
          className={inputClass}
          value={genre}
          onChange={(e) => setGenre(e.target.value)}
          maxLength={100}
        />
        {errors.genre && <p className={errorClass}>{errors.genre}</p>}
      </div>
      <div>
        <label className={labelClass} htmlFor="rating">Rating (1.0 – 10.0)</label>
        <input
          id="rating"
          type="number"
          className={inputClass}
          value={rating}
          onChange={(e) => setRating(e.target.value)}
          min={1}
          max={10}
          step={0.1}
        />
        {errors.rating && <p className={errorClass}>{errors.rating}</p>}
      </div>
      <div>
        <label className={labelClass} htmlFor="watched_date">Watched Date</label>
        <input
          id="watched_date"
          type="date"
          className={inputClass}
          value={watchedDate}
          onChange={(e) => setWatchedDate(e.target.value)}
        />
        {errors.watched_date && <p className={errorClass}>{errors.watched_date}</p>}
      </div>
      <div>
        <label className={labelClass} htmlFor="notes">Notes</label>
        <textarea
          id="notes"
          className={`${inputClass} resize-y min-h-[100px]`}
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          maxLength={1000}
        />
        {errors.notes && <p className={errorClass}>{errors.notes}</p>}
      </div>
      <button
        type="submit"
        disabled={isLoading}
        className="w-full bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-400 text-white font-medium py-2 rounded-md transition-colors flex items-center justify-center gap-2"
      >
        {isLoading && (
          <span className="w-4 h-4 border-2 border-white/40 border-t-white rounded-full animate-spin" aria-hidden="true" />
        )}
        {isLoading ? 'Saving...' : 'Save Movie'}
      </button>
    </form>
  )
}
