export default function Loading() {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="space-y-4">
          <div className="flex justify-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" />
          </div>
          <p className="text-gray-600 text-center">Loading your news feed...</p>
        </div>
      </div>
    );
  }