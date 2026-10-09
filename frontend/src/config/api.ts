/**
 * CAMPUSLINK Centralized API Configuration
 *
 * Configured using VITE_API_URL, defaulting to the deployed Render backend:
 * https://campuslink-ow5y.onrender.com
 */

export const API_BASE_URL: string = (
  (import.meta as any).env?.VITE_API_URL ||
  (import.meta as any).env?.VITE_API_BASE_URL ||
  'https://campuslink-ow5y.onrender.com'
).replace(/\/+$/, '');
