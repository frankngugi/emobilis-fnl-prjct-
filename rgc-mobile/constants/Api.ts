// WiFi mode: phone and laptop must be on the same WiFi network
export const BASE_URL = 'http://192.168.88.47:8000';
export const API_URL = `${BASE_URL}/api`;

// Church WhatsApp number for direct contact
export const CHURCH_WHATSAPP = '+254712760740';
export const CHURCH_WA_LINK = `https://wa.me/254712760740?text=Hello%20RGC%20Nyahururu`;

// Social media links (update with real handles)
export const SOCIAL = {
  facebook: 'https://www.facebook.com/YOUR_CHURCH_PAGE',
  instagram: 'https://www.instagram.com/YOUR_CHURCH_PAGE',
  youtube: 'https://www.youtube.com/@YOUR_CHANNEL',
  linkedin: 'https://www.linkedin.com/company/YOUR_PAGE',
  twitter: 'https://twitter.com/YOUR_PAGE',
};

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

  // Chat
  CHAT_ROOMS: `${API_URL}/chat/rooms/`,
  CHAT_MESSAGES: (id: number) => `${API_URL}/chat/rooms/${id}/messages/`,
  CHAT_SEND: (id: number) => `${API_URL}/chat/rooms/${id}/send/`,

  // Push notifications
  PUSH_REGISTER: `${API_URL}/notifications/register/`,
  PUSH_UNREGISTER: `${API_URL}/notifications/unregister/`,
};
