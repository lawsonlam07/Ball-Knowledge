// Temporary in-memory storage for video file during page navigation
// This persists during client-side navigation in Next.js

let currentVideoFile: File | null = null

export function setVideoFile(file: File | null) {
  currentVideoFile = file
}

export function getVideoFile(): File | null {
  return currentVideoFile
}

export function clearVideoFile() {
  currentVideoFile = null
}
