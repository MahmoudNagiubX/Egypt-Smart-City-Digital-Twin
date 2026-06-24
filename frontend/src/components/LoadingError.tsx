import React from "react";
import { Alert, AlertTitle, AlertDescription } from "@/components/ui/alert";
import { Skeleton } from "@/components/ui/skeleton";
import { ShieldAlert } from "lucide-react";

export const LoadingSpinner: React.FC<{ message?: string }> = ({ message = "Loading dashboard data..." }) => {
  return (
    <div className="flex w-full max-w-sm flex-col gap-4 rounded-xl border bg-card p-5 shadow-lg">
      <div className="flex items-center gap-3">
        <Skeleton className="size-10 rounded-xl" />
        <div className="flex flex-1 flex-col gap-2">
          <Skeleton className="h-3 w-32" />
          <Skeleton className="h-2.5 w-48" />
        </div>
      </div>
      <p className="text-xs font-medium text-muted-foreground">{message}</p>
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
