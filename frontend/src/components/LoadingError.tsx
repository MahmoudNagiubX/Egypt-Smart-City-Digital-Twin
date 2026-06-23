import React from "react";
import { Alert, AlertTitle, AlertDescription } from "@/components/ui/alert";
import { Skeleton } from "@/components/ui/skeleton";
import { ShieldAlert } from "lucide-react";

export const LoadingSpinner: React.FC<{ message?: string }> = ({ message = "Loading dashboard data..." }) => {
  return (
    <div className="flex flex-col items-center justify-center gap-4 p-8">
      <div className="size-8 animate-spin rounded-full border-2 border-accent border-b-primary" />
      <p className="text-sm font-medium text-muted-foreground">{message}</p>
    </div>
  );
};

export const LoadingSkeleton: React.FC = () => {
  return (
    <div className="flex flex-col gap-4 p-4">
      <Skeleton className="h-8 w-[250px]" />
      <Skeleton className="h-[125px] w-full rounded-xl" />
      <div className="flex flex-col gap-2">
        <Skeleton className="h-4 w-[200px]" />
        <Skeleton className="h-4 w-[150px]" />
      </div>
    </div>
  );
};

export const ErrorDisplay: React.FC<{ title?: string; message: string }> = ({ 
  title = "API Connection Error", 
  message 
}) => {
  return (
    <Alert variant="destructive" className="bg-white shadow-lg">
      <ShieldAlert />
      <AlertTitle className="font-bold">{title}</AlertTitle>
      <AlertDescription className="mt-1 text-xs">
        {message}. Ensure the backend service is running locally at http://127.0.0.1:8000.
      </AlertDescription>
    </Alert>
  );
};
