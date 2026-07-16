import { create } from "zustand";

interface User {
  username: string;
  role: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  login: (username: string, token: string, role: string) => void;
  logout: () => void;
  isAuthenticated: () => boolean;
}

export const useAuth = create<AuthState>((set, get) => ({
  user: localStorage.getItem("user") ? JSON.parse(localStorage.getItem("user")!) : null,
  token: localStorage.getItem("token"),
  login: (username, token, role) => {
    const userObj = { username, role };
    localStorage.setItem("token", token);
    localStorage.setItem("user", JSON.stringify(userObj));
    set({ user: userObj, token });
  },
  logout: () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    set({ user: null, token: null });
  },
  isAuthenticated: () => !!get().token,
}));
