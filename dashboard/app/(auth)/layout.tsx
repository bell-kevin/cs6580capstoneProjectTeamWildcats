export const dynamic = "force-dynamic";

import { ThemeProvider } from "@/components/theme-provider";

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <ThemeProvider>{children}</ThemeProvider>;
}
