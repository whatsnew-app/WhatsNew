import { useState } from 'react';
import Image from 'next/image';
import { ChevronDown } from 'lucide-react';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import type { NewsArticle } from '@/types/news';
import { formatDistanceToNow } from 'date-fns';

interface NewsCardProps {
  article: NewsArticle;
  displayStyle?: 'card' | 'rectangle' | 'highlight';
}

export function NewsCard({ article, displayStyle = 'card' }: NewsCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const formattedDate = formatDistanceToNow(new Date(article.published_date), { 
    addSuffix: true 
  });

  const renderContent = () => {
    if (article.content.startsWith('-')) {
      // Handle bullet points
      const points = article.content.split('\n').filter(point => point.trim());
      return (
        <ul className="list-disc list-inside space-y-2">
          {points.map((point, index) => (
            <li key={index}>{point.replace(/^-\s*/, '')}</li>
          ))}
        </ul>
      );
    }
    return <div dangerouslySetInnerHTML={{ __html: article.content }} />;
  };

  return (
    <Card className="mb-4">
      <CardHeader className="space-y-0">
        <div className="flex justify-between items-start mb-2">
          <span className="text-gray-600 text-sm">{formattedDate}</span>
          {article.prompt_name && (
            <span className="px-2 py-1 bg-blue-100 text-blue-800 text-sm rounded">
              {article.prompt_name}
            </span>
          )}
        </div>
        <h2 className="text-xl font-bold mb-4">{article.title}</h2>
      </CardHeader>
      {article.image_url && (
        <div className="relative h-48 w-full">
          <Image
            src={article.image_url}
            alt={article.title}
            fill
            className="object-cover"
          />
        </div>
      )}
      <CardContent>
        <div className="prose max-w-none">
          {isExpanded ? (
            renderContent()
          ) : (
            <p>{article.summary || article.content.slice(0, 200)}...</p>
          )}
        </div>
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="text-blue-600 hover:text-blue-800 mt-2 flex items-center"
        >
          {isExpanded ? 'Show less' : 'Read more'}
          <ChevronDown
            className={`ml-1 transform transition-transform ${
              isExpanded ? 'rotate-180' : ''
            }`}
          />
        </button>
      </CardContent>
      <div className="bg-gray-50 px-4 py-2 rounded-b-lg">
        <div className="flex items-center justify-between text-sm text-gray-600">
          <span>♦ AI generated content</span>
          {article.source_urls && article.source_urls.length > 0 && (
            <a 
              href={article.source_urls[0]} 
              target="_blank" 
              rel="noopener noreferrer"
              className="hover:text-blue-600"
            >
              View source
            </a>
          )}
        </div>
      </div>
    </Card>
  );
}