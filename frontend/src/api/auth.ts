import apiClient from './axios'
import type { LoginRequest, RegisterRequest, Token, UserResponse } from '../types'

export async function register(data: RegisterRequest): Promise<UserResponse> {
  const response = await apiClient.post<UserResponse>('/auth/register', data)
  return response.data
}

export async function login(data: LoginRequest): Promise<Token> {
  const response = await apiClient.post<Token>('/auth/login', data)
  return response.data
}
