import type React from "react"
import type { Metadata } from "next"
import { GeistSans } from "geist/font/sans"
import { GeistMono } from "geist/font/mono"
import "./globals.css"

export const metadata: Metadata = {
  title: "FinGuard Frontend",
  description: "E2E Encrypted Financial Gateway",
  generator: "v0.app",
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <head>
        <style>{`
html {
  font-family: ${GeistSans.style.fontFamily};
  --font-sans: ${GeistSans.variable};
  --font-mono: ${GeistMono.variable};
}
        `}</style>
      </head>
      <body className="min-h-screen bg-background text-foreground">
        <div className="max-w-6xl mx-auto p-6 space-y-6">
          <header className="flex items-center justify-between">
            <h1 className="text-2xl font-semibold">FinGuard Frontend</h1>
          </header>
          {children}
        </div>
      </body>
    </html>
  )
}
