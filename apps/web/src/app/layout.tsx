import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "CareerOS",
  description: "Career and job application management platform",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
