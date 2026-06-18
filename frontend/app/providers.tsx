"use client";

import { SWRConfig } from "swr";
import { AuthProvider } from "@/lib/auth";
import { ToastProvider } from "@/lib/toast";

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <SWRConfig
      value={{
        revalidateOnFocus: false,
        shouldRetryOnError: false,
        dedupingInterval: 4000,
      }}
    >
      <ToastProvider>
        <AuthProvider>{children}</AuthProvider>
      </ToastProvider>
    </SWRConfig>
  );
}
