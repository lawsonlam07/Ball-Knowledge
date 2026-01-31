"use client"

import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Home, Loader2, Play } from "lucide-react"

export function DevNavigation() {
  return (
    <div className="fixed bottom-4 right-4 flex gap-2 z-50">
      <Link href="/">
        <Button variant="outline" size="sm" className="shadow-lg">
          <Home className="h-4 w-4 mr-2" />
          Upload
        </Button>
      </Link>
      <Link href="/loading-page">
        <Button variant="outline" size="sm" className="shadow-lg">
          <Loader2 className="h-4 w-4 mr-2" />
          Loading
        </Button>
      </Link>
      <Link href="/viewer">
        <Button variant="outline" size="sm" className="shadow-lg">
          <Play className="h-4 w-4 mr-2" />
          Viewer
        </Button>
      </Link>
    </div>
  )
}
