import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { createMovie } from '../api/movies'
import type { MovieCreate } from '../types'
import MovieForm from '../components/MovieForm'
import { AxiosError } from 'axios'

export default function AddMoviePage() {
  const navigate = useNavigate()
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleSubmit(data: MovieCreate) {
    setIsLoading(true)
    setError('')
    try {
      await createMovie(data)
      navigate('/')
    } catch (err) {
      if (err instanceof AxiosError && err.response) {
        const detail = err.response.data?.detail
        setError(typeof detail === 'string' ? detail : 'Failed to create movie.')
      } else {
        setError('Unable to connect. Please try again.')
      }
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="max-w-xl mx-auto">
      <div className="flex items-center gap-3 mb-6">
        <Link to="/" className="text-gray-500 hover:text-gray-700 text-sm">← Back</Link>
        <h1 className="text-2xl font-bold text-gray-900">Add Movie</h1>
      </div>
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 rounded-md px-4 py-3 mb-4 text-sm" role="alert">
          {error}
        </div>
      )}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <MovieForm onSubmit={handleSubmit} isLoading={isLoading} />
      </div>
    </div>
  )
}
