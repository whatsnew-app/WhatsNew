export interface User {
    id: string;
    email: string;
    full_name?: string;
    is_active: boolean;
    is_superuser: boolean;
    created_at: string;
    updated_at: string;
  }
  
  export interface LoginCredentials {
    username: string;
    password: string;
  }
  
  export interface RegisterCredentials {
    email: string;
    password: string;
    full_name?: string;
  }
  
  export interface AuthTokens {
    access_token: string;
    refresh_token: string;
    token_type: string;
  }
  
  export interface AuthState {
    user: User | null;
    isLoading: boolean;
    isAuthenticated: boolean;
    error: string | null;
  }