// ─── Server Configuration ─────────────────────────────────────────────────────
//
// DEVELOPMENT (testing on phone with laptop):
//   Set BASE_URL to your laptop's WiFi IP, e.g. 'http://192.168.88.47:8000'
//   Run: python manage.py runserver 0.0.0.0:8000
//
// PRODUCTION (APK for end users — no laptop needed):
//   Set BASE_URL to your Render URL after deploying
//   e.g. 'https://rgc-nyahururu-cms.onrender.com'
//
// ─────────────────────────────────────────────────────────────────────────────

export const BASE_URL = 'https://rgc-nyahururu-cms.onrender.com';

// ← Change the line above to your laptop IP for local dev
//   e.g.  export const BASE_URL = 'http://192.168.88.47:8000';

export const API_URL = `${BASE_URL}/api`;

// Church WhatsApp & social links
export const CHURCH_WHATSAPP = '+254712760740';
export const CHURCH_WA_LINK = `https://wa.me/254712760740?text=Hello%20RGC%20Nyahururu`;

export const SOCIAL = {
  facebook:  'https://www.facebook.com/YOUR_CHURCH_PAGE',
  instagram: 'https://www.instagram.com/YOUR_CHURCH_PAGE',
  youtube:   'https://www.youtube.com/@YOUR_CHANNEL',
  linkedin:  'https://www.linkedin.com/company/YOUR_PAGE',
  twitter:   'https://twitter.com/YOUR_PAGE',
};

export const ENDPOINTS = {
  // Auth
  LOGIN:           `${API_URL}/auth/login/`,
  REGISTER:        `${API_URL}/auth/register/`,
  REFRESH:         `${API_URL}/auth/refresh/`,
  PROFILE:         `${API_URL}/auth/profile/`,
  CHANGE_PASSWORD: `${API_URL}/auth/change-password/`,

  // Content
  ANNOUNCEMENTS: `${API_URL}/announcements/`,
  EVENTS:        `${API_URL}/events/`,
  MY_EVENTS:     `${API_URL}/events/my/`,
  HYMNS:         `${API_URL}/hymns/`,
  BIBLE:         `${API_URL}/bible/`,
  GROUPS:        `${API_URL}/groups/`,
  GALLERY:       `${API_URL}/gallery/`,
  VIDEOS:        `${API_URL}/videos/`,
  PAYMENTS:      `${API_URL}/payments/`,
  PAY:           `${API_URL}/payments/initiate/`,

  // Admin
  DASHBOARD:   `${API_URL}/admin/dashboard/`,
  ALL_MEMBERS: `${API_URL}/admin/members/`,
  CATEGORIES:  `${API_URL}/categories/`,

  // Chat
  CHAT_ROOMS:    `${API_URL}/chat/rooms/`,
  CHAT_MESSAGES: (id: number) => `${API_URL}/chat/rooms/${id}/messages/`,
  CHAT_SEND:     (id: number) => `${API_URL}/chat/rooms/${id}/send/`,

  // Push notifications
  PUSH_REGISTER:   `${API_URL}/notifications/register/`,
  PUSH_UNREGISTER: `${API_URL}/notifications/unregister/`,
};
