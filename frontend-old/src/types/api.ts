export interface ApiError {
    message: string;
    code?: string;
    details?: Record<string, any>;
  }
  
  export interface PaginationParams {
    skip?: number;
    limit?: number;
  }
  
  export interface DateFilterParams extends PaginationParams {
    date_filter?: string;
  }
  
  export interface ApiResponse<T> {
    data: T;
    error?: ApiError;
  }
  
  export interface PaginatedResponse<T> {
    items: T[];
    total: number;
    skip: number;
    limit: number;
  }