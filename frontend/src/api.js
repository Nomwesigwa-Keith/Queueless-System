const API_URL = import.meta.env.VITE_API_URL || "/api";

async function request(path, options = {}) {
  const token = localStorage.getItem("queueless_token");
  let response;
  try {
    response = await fetch(`${API_URL}${path}`, {
      headers: { "Content-Type": "application/json", ...(token ? { Authorization: `Bearer ${token}` } : {}) },
      ...options,
    });
  } catch {
    throw new Error("Cannot reach the backend. Confirm Django is running at http://127.0.0.1:8000.");
  }
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const messages = Object.values(data).flatMap((value) => Array.isArray(value) ? value : [value]).filter(Boolean);
    throw new Error(messages.join(" ") || `Request failed (${response.status})`);
  }
  return data;
}

export const api = {
  login: (email, password) => request("/auth/token/", { method: "POST", body: JSON.stringify({ email, password }) }),
  register: (payload) => request("/auth/register/", { method: "POST", body: JSON.stringify(payload) }),
  registerBusiness: (payload) => request("/auth/business-register/", { method: "POST", body: JSON.stringify(payload) }),
  businessesDirectory: (query = "") => request(`/directory/businesses/${query ? `?q=${encodeURIComponent(query)}` : ""}`),
  me: () => request("/auth/me/"),
  join: (payload) => request("/tickets/", { method: "POST", body: JSON.stringify(payload) }),
  myTicket: (id) => request(`/tickets/${id}/`),
  queue: (service) => request(service ? `/tickets/?service=${encodeURIComponent(service)}` : "/tickets/"),
  updateTicket: (id, status) => request(`/tickets/${id}/status/`, { method: "POST", body: JSON.stringify({ status }) }),
  cancelTicket: (id) => request(`/tickets/${id}/cancel/`, { method: "POST" }),
  business: () => request("/business/"),
  updateBusiness: (payload) => request("/business/", { method: "PATCH", body: JSON.stringify(payload) }),
  pauseBusiness: (paused) => request("/business/pause/", { method: "POST", body: JSON.stringify({ paused }) }),
  staff: () => request("/business/staff/"),
  assignStaff: (email) => request("/business/staff/", { method: "POST", body: JSON.stringify({ email }) }),
  stats: () => request("/business/stats/"),
  approveBusiness: (id, status) => request(`/admin/businesses/${id}/status/`, { method: "POST", body: JSON.stringify({ status }) }),
  changePassword: (payload) => request("/auth/password/change/", { method: "POST", body: JSON.stringify(payload) }),
  requestPasswordReset: (email) => request("/auth/password/reset/", { method: "POST", body: JSON.stringify({ email }) }),
  confirmPasswordReset: (payload) => request("/auth/password/reset/confirm/", { method: "POST", body: JSON.stringify(payload) }),
  businessStats: () => request("/business/stats/"),
  businesses: () => request("/admin/businesses/"),
};
