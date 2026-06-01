import * as React from "react";

export function Badge({ className = "", children, ...props }: React.HTMLAttributes<HTMLSpanElement>) {
  return (
    <span
      className={`inline-flex items-center rounded-md bg-secondary px-2 py-0.5 text-xs font-medium text-secondary-foreground ${className}`}
      {...props}
    >
      {children}
    </span>
  );
}
