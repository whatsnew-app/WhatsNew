export interface Prompt {
    id: string;
    name: string;
    content: string;
    type: PromptType;
    generate_image: boolean;
    display_style: DisplayStyle;
    news_sources: string[];
    template_id: string;
    user_id: string;
    created_at: string;
    updated_at: string;
  }
  
  export interface PromptCreate {
    name: string;
    content: string;
    type: PromptType;
    generate_image?: boolean;
    display_style: DisplayStyle;
    news_sources: string[];
    template_id: string;
  }
  
  export interface PromptUpdate {
    name?: string;
    content?: string;
    type?: PromptType;
    generate_image?: boolean;
    display_style?: DisplayStyle;
    news_sources?: string[];
    template_id?: string;
  }
  
  export interface Template {
    id: string;
    name: string;
    description?: string;
    template_content: string;
    is_active: boolean;
    created_at: string;
    updated_at: string;
  }