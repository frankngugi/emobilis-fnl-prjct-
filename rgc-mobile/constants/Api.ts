// Change this to your server's IP when testing on a physical device
// Use your computer's local IP (not localhost) e.g. http://192.168.1.100:8000
// For production, change to your deployed URL
// Your computer's WiFi IP — phone uses this to reach Django
export const BASE_URL = 'http://192.168.88.47:8000';
export const API_URL = `${BASE_URL}/api`;

export const ENDPOINTS = {
  // Auth
  LOGIN: `${API_URL}/auth/login/`,
  REGISTER: `${API_URL}/auth/register/`,
  REFRESH: `${API_URL}/auth/refresh/`,
  PROFILE: `${API_URL}/auth/profile/`,
  CHANGE_PASSWORD: `${API_URL}/auth/change-password/`,

  // Content
  ANNOUNCEMENTS: `${API_URL}/announcements/`,
  EVENTS: `${API_URL}/events/`,
  MY_EVENTS: `${API_URL}/events/my/`,
  HYMNS: `${API_URL}/hymns/`,
  BIBLE: `${API_URL}/bible/`,
  GROUPS: `${API_URL}/groups/`,
  GALLERY: `${API_URL}/gallery/`,
  VIDEOS: `${API_URL}/videos/`,
  PAYMENTS: `${API_URL}/payments/`,
  PAY: `${API_URL}/payments/initiate/`,

  // Admin
  DASHBOARD: `${API_URL}/admin/dashboard/`,
  ALL_MEMBERS: `${API_URL}/admin/members/`,
  CATEGORIES: `${API_URL}/categories/`,
};
