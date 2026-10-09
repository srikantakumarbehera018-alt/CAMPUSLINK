/**
 * CAMPUSLINK Centralized API Configuration
 *
 * In local development, defaults to http://localhost:8000 (FastAPI backend).
 * When deploying frontend, set VITE_API_BASE_URL to your deployed backend URL.
 * Example: VITE_API_BASE_URL=https://campuslink-backend.vercel.app
 */

export const API_BASE_URL: string = (
  (import.meta as any).env?.VITE_API_BASE_URL ||
  (import.meta as any).env?.VITE_API_URL ||
  'http://localhost:8000'
).replace(/\/+$/, '');
