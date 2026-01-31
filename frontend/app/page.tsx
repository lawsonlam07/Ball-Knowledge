"use client"

import { useState, useRef } from "react"
import Image from "next/image"
import { Upload, Link as LinkIcon } from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectGroup, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Separator } from "@/components/ui/separator"

export default function Page() {
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [uploadMethod, setUploadMethod] = useState<"file" | "url">("file")
  const [videoFile, setVideoFile] = useState<File | null>(null)
  const [videoUrl, setVideoUrl] = useState("")
  const [isDragging, setIsDragging] = useState(false)

  // Commentator customization state
  const [voice, setVoice] = useState("")
  const [expertiseLevel, setExpertiseLevel] = useState("")
  const [commentaryStyle, setCommentaryStyle] = useState("")

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)

    const files = e.dataTransfer.files
    if (files.length > 0) {
      const file = files[0]
      if (file.type.startsWith("video/")) {
        setVideoFile(file)
        setUploadMethod("file")
      }
    }
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (files && files.length > 0) {
      setVideoFile(files[0])
      setUploadMethod("file")
    }
  }

  const handleClickUpload = () => {
    fileInputRef.current?.click()
  }

  const handleSubmit = () => {
    // TODO: Navigate to loading page and submit to backend
    console.log({
      uploadMethod,
      videoFile: videoFile?.name,
      videoUrl,
      voice,
      expertiseLevel,
      commentaryStyle
    })
  }

  const canSubmit = (uploadMethod === "file" && videoFile) || (uploadMethod === "url" && videoUrl)

  return (
    <div className="min-h-screen bg-linear-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800 p-6 flex items-center justify-center">
      <Card className="w-full max-w-3xl">
        <CardHeader className="text-center">
          <div className="flex items-center justify-center gap-3 mb-2">
            <Image src="/file.svg" alt="Ball Knowledge Logo" width={50} height={50} />
            <CardTitle className="text-3xl font-bold">Ball Knowledge</CardTitle>
          </div>
          <CardDescription className="text-base">
            Upload your tennis match video and let AI bring it to life with professional commentary
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Upload Method Toggle */}
          <div className="flex gap-2">
            <Button
              variant={uploadMethod === "file" ? "default" : "outline"}
              className="flex-1"
              onClick={() => setUploadMethod("file")}
            >
              <Upload className="mr-2 h-4 w-4" />
              Upload File
            </Button>
            <Button
              variant={uploadMethod === "url" ? "default" : "outline"}
              className="flex-1"
              onClick={() => setUploadMethod("url")}
            >
              <LinkIcon className="mr-2 h-4 w-4" />
              Video URL
            </Button>
          </div>

          {/* File Upload Section */}
          {uploadMethod === "file" && (
            <div
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={videoFile ? undefined : handleClickUpload}
              className={`border-2 border-dashed rounded-lg p-12 text-center transition-colors ${
                isDragging
                  ? "border-primary bg-primary/5"
                  : "border-slate-300 dark:border-slate-700"
              } ${!videoFile ? "cursor-pointer hover:border-primary hover:bg-primary/5" : ""}`}
            >
              {videoFile ? (
                <div className="space-y-2">
                  <p className="text-sm font-medium text-slate-700 dark:text-slate-300">
                    Selected: {videoFile.name}
                  </p>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setVideoFile(null)}
                  >
                    Remove
                  </Button>
                </div>
              ) : (
                <div className="space-y-4">
                  <Upload className="h-12 w-12 mx-auto text-slate-400" />
                  <div>
                    <p className="text-base font-medium text-slate-700 dark:text-slate-300">
                      Drag and drop your video here
                    </p>
                    <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
                      or click to browse
                    </p>
                  </div>
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="video/*"
                    onChange={handleFileChange}
                    className="hidden"
                  />
                </div>
              )}
            </div>
          )}

          {/* URL Input Section */}
          {uploadMethod === "url" && (
            <div className="space-y-2">
              <Label htmlFor="video-url">Video URL</Label>
              <Input
                id="video-url"
                placeholder="https://youtube.com/watch?v=... or direct video URL"
                value={videoUrl}
                onChange={(e) => setVideoUrl(e.target.value)}
              />
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Supports YouTube, Vimeo, and direct video links
              </p>
            </div>
          )}

          <Separator />

          {/* Commentator Customization */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Customize Your Commentator</h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="voice">Voice</Label>
                <Select value={voice} onValueChange={setVoice}>
                  <SelectTrigger id="voice">
                    <SelectValue placeholder="Select a voice" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectGroup>
                      <SelectItem value="professional-male">Professional Male</SelectItem>
                      <SelectItem value="professional-female">Professional Female</SelectItem>
                      <SelectItem value="enthusiastic-male">Enthusiastic Male</SelectItem>
                      <SelectItem value="enthusiastic-female">Enthusiastic Female</SelectItem>
                      <SelectItem value="british-male">British Male</SelectItem>
                      <SelectItem value="british-female">British Female</SelectItem>
                    </SelectGroup>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="expertise">Your Tennis Knowledge</Label>
                <Select value={expertiseLevel} onValueChange={setExpertiseLevel}>
                  <SelectTrigger id="expertise">
                    <SelectValue placeholder="How well do you know tennis?" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectGroup>
                      <SelectItem value="beginner">Beginner - Explain everything</SelectItem>
                      <SelectItem value="intermediate">Intermediate - Some basics</SelectItem>
                      <SelectItem value="advanced">Advanced - Technical details</SelectItem>
                      <SelectItem value="expert">Expert - Pro-level analysis</SelectItem>
                    </SelectGroup>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="style">Commentary Style</Label>
                <Select value={commentaryStyle} onValueChange={setCommentaryStyle}>
                  <SelectTrigger id="style">
                    <SelectValue placeholder="Choose commentary style" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectGroup>
                      <SelectItem value="play-by-play">Play-by-Play</SelectItem>
                      <SelectItem value="analytical">Analytical & Strategic</SelectItem>
                      <SelectItem value="entertaining">Entertaining & Fun</SelectItem>
                      <SelectItem value="educational">Educational</SelectItem>
                      <SelectItem value="emotional">Emotional & Dramatic</SelectItem>
                    </SelectGroup>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>

          {/* Submit Button */}
          <Button
            className="w-full"
            size="lg"
            onClick={handleSubmit}
            disabled={!canSubmit}
          >
            Generate Commentary
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}
