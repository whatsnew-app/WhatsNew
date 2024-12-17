// src/types/auth.ts

// User types
export interface User {
    id: string;
    email: string;
    full_name?: string;
    is_active: boolean;
    is_superuser: boolean;
    created_at: string;
    updated_at: string;
    last_login?: string;
    preferences?: UserPreferences;
    permissions?: string[];
  }
  
  export interface UserPreferences {
    theme?: 'light' | 'dark' | 'system';
    emailNotifications?: boolean;
    newsCategories?: string[];
    language?: string;
    timezone?: string;
  }
  
  // Authentication state
  export interface AuthState {
    user: User | null;
    isLoading: boolean;
    isAuthenticated: boolean;
    error: string | null;
  }
  
  // Login types
  export interface LoginCredentials {
    username: string;
    password: string;
    remember?: boolean;
  }
  
  export interface LoginResponse {
    access_token: string;
    refresh_token: string;
    token_type: string;
    expires_in: number;
  }
  
  // Register types
  export interface RegisterCredentials {
    email: string;
    password: string;
    full_name?: string;
    terms_accepted: boolean;
  }
  
  export interface RegisterResponse {
    id: string;
    email: string;
    full_name?: string;
  }
  
  // Token types
  export interface AuthTokens {
    access_token: string;
    refresh_token: string;
    token_type: string;
    expires_in: number;
  }
  
  export interface RefreshTokenRequest {
    refresh_token: string;
  }
  
  // Password reset types
  export interface PasswordResetRequest {
    email: string;
  }
  
  export interface PasswordResetConfirm {
    token: string;
    password: string;
    password_confirm: string;
  }
  
  // Profile update types
  export interface ProfileUpdateRequest {
    full_name?: string;
    email?: string;
    current_password?: string;
    new_password?: string;
    preferences?: Partial<UserPreferences>;
  }
  
  // Error types
  export interface AuthError {
    message: string;
    code: string;
    field?: string;
  }
  
  // JWT Token payload
  export interface JWTPayload {
    sub: string;
    email: string;
    exp: number;
    iat: number;
    is_superuser: boolean;
    permissions?: string[];
  }
  
  // Session types
  export interface Session {
    user: User;
    tokens: AuthTokens;
    expiresAt: number;
  }
  
  // Auth provider context
  export interface AuthContextValue {
    user: User | null;
    isLoading: boolean;
    isAuthenticated: boolean;
    error: string | null;
    login: (credentials: LoginCredentials) => Promise<void>;
    register: (data: RegisterCredentials) => Promise<void>;
    logout: () => void;
    resetPassword: (email: string) => Promise<void>;
    updateProfile: (data: ProfileUpdateRequest) => Promise<void>;
    refreshToken: () => Promise<boolean>;
    clearError: () => void;
  }
  
  // Permission types
  export type Permission = 
    | 'news:read'
    | 'news:write'
    | 'prompts:read'
    | 'prompts:write'
    | 'admin:access'
    | 'templates:manage'
    | 'tasks:manage';
  
  // Role types
  export type UserRole = 
    | 'user'
    | 'admin'
    | 'editor'
    | 'contributor';
  
  // Auth configuration
  export interface AuthConfig {
    tokenRefreshThreshold: number;  // Seconds before token expiry to trigger refresh
    loginRedirectUrl: string;
    logoutRedirectUrl: string;
    publicPaths: string[];
    unauthorizedRedirectUrl: string;
  }
  
  // Helper type for permission checking
  export type PermissionCheck = (permission: Permission) => boolean;
  
  // Helper type for role checking
  export type RoleCheck = (role: UserRole) => boolean;