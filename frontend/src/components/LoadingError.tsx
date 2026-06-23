import React from "react";
import { Alert, AlertTitle, AlertDescription } from "@/components/ui/alert";
import { Skeleton } from "@/components/ui/skeleton";
import { ShieldAlert } from "lucide-react";

export const LoadingSpinner: React.FC<{ message?: string }> = ({ message = "Loading dashboard data..." }) => {
  return (
    <div className="flex flex-col items-center justify-center p-8 space-y-4">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyan-500"></div>
      <p className="text-sm text-slate-400 font-medium">{message}</p>
    </div>
  );
};

export const LoadingSkeleton: React.FC = () => {
  return (
    <div className="space-y-4 p-4">
      <Skeleton className="h-8 w-[250px] bg-slate-800" />
      <Skeleton className="h-[125px] w-full rounded-xl bg-slate-800" />
      <div className="space-y-2">
        <Skeleton className="h-4 w-[200px] bg-slate-800" />
        <Skeleton className="h-4 w-[150px] bg-slate-800" />
      </div>
    </div>
  );
};

export const ErrorDisplay: React.FC<{ title?: string; message: string }> = ({ 
  title = "API Connection Error", 
  message 
}) => {
  return (
    <Alert variant="destructive" className="bg-red-950/80 border-red-900 text-red-200">
      <ShieldAlert className="h-4 w-4 stroke-red-400" />
      <AlertTitle className="font-bold">{title}</AlertTitle>
      <AlertDescription className="text-xs text-red-300 mt-1">
        {message}. Ensure the backend service is running locally at http://127.0.0.1:8000.
      </AlertDescription>
    </Alert>
  );
};
