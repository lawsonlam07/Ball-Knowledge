"use client"

import { useState, useRef, useMemo, useEffect, useCallback } from "react"
import { useSearchParams } from "next/navigation"
import Image from "next/image"
import { Button } from "@/components/ui/button"
import { Slider } from "@/components/ui/slider"
import { Play, Pause, Volume2, VolumeX, Maximize, SkipBack, SkipForward, Download } from "lucide-react"

interface CommentarySegment {
  timestamp: number
  text: string
  type: "play" | "analysis" | "excitement"
}

// Mock commentary data - replace with actual data from backend
const commentarySegments: CommentarySegment[] = [
  { timestamp: 0, text: "Welcome to this exciting tennis match! Both players are warming up at the baseline.", type: "play" },
  { timestamp: 5, text: "Great serve by the player on the right! Notice the excellent toss and shoulder rotation.", type: "analysis" },
  { timestamp: 10, text: "What a rally! Both players showing incredible footwork and court coverage!", type: "excitement" },
  { timestamp: 15, text: "The backhand crosscourt winner! Absolutely stunning shot placement.", type: "excitement" },
]

export default function ViewerPage() {
  const searchParams = useSearchParams()
  const videoRef = useRef<HTMLVideoElement>(null)

  // Get video source from URL params or use default
  const videoSource = useMemo(() => {
    return searchParams.get('video') || "/tennis.mp4"
  }, [searchParams])

  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)
  const [volume, setVolume] = useState(100)
  const [isMuted, setIsMuted] = useState(false)
  const [showVolumeSlider, setShowVolumeSlider] = useState(false)
  const [showControls, setShowControls] = useState(false)

  // Find current commentary based on video time
  const currentCommentary = useMemo(() => {
    return commentarySegments
      .filter(seg => seg.timestamp <= currentTime)
      .sort((a, b) => b.timestamp - a.timestamp)[0] || null
  }, [currentTime])

  const togglePlay = useCallback(() => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause()
      } else {
        videoRef.current.play()
      }
      setIsPlaying(!isPlaying)
    }
  }, [isPlaying])

  const handleTimeUpdate = () => {
    if (videoRef.current) {
      setCurrentTime(videoRef.current.currentTime)
      // Fallback: set duration if it hasn't been set yet
      if (duration === 0 && videoRef.current.duration) {
        setDuration(videoRef.current.duration)
      }
    }
  }

  const handleLoadedMetadata = () => {
    if (videoRef.current && videoRef.current.duration) {
      setDuration(videoRef.current.duration)
    }
  }

  const handleCanPlay = () => {
    if (videoRef.current && videoRef.current.duration && duration === 0) {
      setDuration(videoRef.current.duration)
    }
  }

  const handleSeek = (value: number[]) => {
    if (videoRef.current) {
      videoRef.current.currentTime = value[0]
      setCurrentTime(value[0])
    }
  }

  const handleVolumeChange = (value: number[]) => {
    const newVolume = value[0]
    setVolume(newVolume)
    if (videoRef.current) {
      videoRef.current.volume = newVolume / 100
    }
    setIsMuted(newVolume === 0)
  }

  const toggleMute = useCallback(() => {
    if (videoRef.current) {
      const newMutedState = !isMuted
      videoRef.current.muted = newMutedState
      setIsMuted(newMutedState)
    }
  }, [isMuted])

  const toggleFullscreen = useCallback(() => {
    if (videoRef.current) {
      if (document.fullscreenElement) {
        document.exitFullscreen()
      } else {
        videoRef.current.requestFullscreen()
      }
    }
  }, [])

  const skipTime = useCallback((seconds: number) => {
    if (videoRef.current) {
      const newTime = videoRef.current.currentTime + seconds
      videoRef.current.currentTime = Math.max(0, Math.min(videoRef.current.duration, newTime))
    }
  }, [])

  const formatTime = (time: number) => {
    const minutes = Math.floor(time / 60)
    const seconds = Math.floor(time % 60)
    return `${minutes}:${seconds.toString().padStart(2, '0')}`
  }

  // YouTube keyboard controls
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Don't trigger if user is typing in an input field
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) {
        return
      }

      switch (e.key.toLowerCase()) {
        case ' ':
        case 'k':
          e.preventDefault()
          togglePlay()
          break
        case 'arrowleft':
          e.preventDefault()
          skipTime(-5)
          break
        case 'arrowright':
          e.preventDefault()
          skipTime(5)
          break
        case 'j':
          e.preventDefault()
          skipTime(-10)
          break
        case 'l':
          e.preventDefault()
          skipTime(10)
          break
        case 'arrowup':
          e.preventDefault()
          setVolume(prev => Math.min(100, prev + 5))
          if (videoRef.current) {
            videoRef.current.volume = Math.min(1, (volume + 5) / 100)
          }
          setIsMuted(false)
          break
        case 'arrowdown':
          e.preventDefault()
          setVolume(prev => Math.max(0, prev - 5))
          if (videoRef.current) {
            videoRef.current.volume = Math.max(0, (volume - 5) / 100)
          }
          break
        case 'm':
          e.preventDefault()
          toggleMute()
          break
        case 'f':
          e.preventDefault()
          toggleFullscreen()
          break
        case '0':
        case '1':
        case '2':
        case '3':
        case '4':
        case '5':
        case '6':
        case '7':
        case '8':
        case '9':
          e.preventDefault()
          if (videoRef.current && duration) {
            const percentage = parseInt(e.key) * 10
            videoRef.current.currentTime = (duration * percentage) / 100
          }
          break
        case 'home':
          e.preventDefault()
          if (videoRef.current) {
            videoRef.current.currentTime = 0
          }
          break
        case 'end':
          e.preventDefault()
          if (videoRef.current && duration) {
            videoRef.current.currentTime = duration
          }
          break
        default:
          break
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isPlaying, volume, duration, togglePlay, skipTime, toggleMute, toggleFullscreen])

  return (
    <div className="min-h-screen bg-linear-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800 p-4 md:p-6">
      <div className="max-w-7xl mx-auto space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Image src="/file.svg" alt="Ball Knowledge Logo" width={50} height={50} />
            <h1 className="text-2xl md:text-3xl font-bold text-slate-900 dark:text-slate-100">
              Ball Knowledge
            </h1>
          </div>
          <Button variant="outline" size="sm">
            <Download className="mr-2 h-4 w-4" />
            Download
          </Button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          {/* Video Player */}
          <div className="lg:col-span-2">
            <div
              className="relative bg-black rounded-lg overflow-hidden group"
              onMouseEnter={() => setShowControls(true)}
              onMouseLeave={() => setShowControls(false)}
            >
              <video
                ref={videoRef}
                className="w-full aspect-video cursor-pointer"
                onTimeUpdate={handleTimeUpdate}
                onLoadedMetadata={handleLoadedMetadata}
                onCanPlay={handleCanPlay}
                onLoadedData={handleLoadedMetadata}
                onClick={togglePlay}
                src={videoSource}
              >
                Your browser does not support the video tag.
              </video>

              {/* Video Overlay - Commentary */}
              {currentCommentary && (
                <div className="absolute bottom-24 left-4 right-4 pointer-events-none">
                  <div className="p-3 rounded-lg bg-black/70 backdrop-blur-md border border-white/20">
                    <p className="text-sm md:text-base font-medium text-white">
                      {currentCommentary.text}
                    </p>
                  </div>
                </div>
              )}

              {/* Video Controls Overlay */}
              <div className={`absolute bottom-0 left-0 right-0 bg-linear-to-t from-black/80 via-black/50 to-transparent p-4 transition-opacity duration-300 ${showControls ? 'opacity-100' : 'opacity-0'}`}>
                {/* Progress Bar */}
                <div className="mb-3">
                  <Slider
                    value={[currentTime]}
                    max={duration || 100}
                    step={0.1}
                    onValueChange={handleSeek}
                    className="cursor-pointer"
                  />
                </div>

                {/* Control Buttons */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-1">
                    <Button
                      variant="ghost"
                      size="icon"
                      className="text-white hover:bg-white/20"
                      onClick={(e) => {
                        e.stopPropagation()
                        togglePlay()
                      }}
                    >
                      {isPlaying ? (
                        <Pause className="h-5 w-5" />
                      ) : (
                        <Play className="h-5 w-5" />
                      )}
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="text-white hover:bg-white/20"
                      onClick={(e) => {
                        e.stopPropagation()
                        skipTime(-10)
                      }}
                    >
                      <SkipBack className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="text-white hover:bg-white/20"
                      onClick={(e) => {
                        e.stopPropagation()
                        skipTime(10)
                      }}
                    >
                      <SkipForward className="h-4 w-4" />
                    </Button>

                    {/* Volume Control */}
                    <div className="relative flex items-center group/volume">
                      <Button
                        variant="ghost"
                        size="icon"
                        className="text-white hover:bg-white/20"
                        onMouseEnter={() => setShowVolumeSlider(true)}
                        onClick={(e) => {
                          e.stopPropagation()
                          toggleMute()
                        }}
                      >
                        {isMuted || volume === 0 ? (
                          <VolumeX className="h-4 w-4" />
                        ) : (
                          <Volume2 className="h-4 w-4" />
                        )}
                      </Button>
                      {showVolumeSlider && (
                        <div
                          className="absolute left-full ml-2 bg-black/90 rounded-lg px-3 py-2"
                          onMouseEnter={() => setShowVolumeSlider(true)}
                          onMouseLeave={() => setShowVolumeSlider(false)}
                        >
                          <Slider
                            value={[volume]}
                            max={100}
                            step={1}
                            onValueChange={handleVolumeChange}
                            className="w-24"
                          />
                        </div>
                      )}
                    </div>

                    {/* Time Display */}
                    <span className="text-xs text-white ml-2">
                      {formatTime(currentTime)} / {formatTime(duration)}
                    </span>
                  </div>

                  <div className="flex items-center gap-1">
                    <Button
                      variant="ghost"
                      size="icon"
                      className="text-white hover:bg-white/20"
                      onClick={(e) => {
                        e.stopPropagation()
                        toggleFullscreen()
                      }}
                    >
                      <Maximize className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Commentary Timeline */}
          <div className="bg-white dark:bg-slate-800 rounded-lg p-4 shadow-sm">
            <h2 className="text-sm font-semibold mb-3 text-slate-600 dark:text-slate-400 uppercase tracking-wide">Commentary</h2>
            <div className="space-y-2 max-h-[600px] overflow-y-auto pr-2">
              {commentarySegments.map((segment, index) => (
                <button
                  key={index}
                  onClick={() => handleSeek([segment.timestamp])}
                  className={`w-full text-left p-3 rounded-lg transition-all hover:bg-slate-100 dark:hover:bg-slate-700 ${
                    currentCommentary?.timestamp === segment.timestamp
                      ? "bg-slate-100 dark:bg-slate-700 border-l-2 border-primary"
                      : ""
                  }`}
                >
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-mono text-slate-500 dark:text-slate-400">
                      {formatTime(segment.timestamp)}
                    </span>
                    <span className="text-xs px-1.5 py-0.5 rounded bg-slate-200 dark:bg-slate-600 text-slate-600 dark:text-slate-300 capitalize">
                      {segment.type}
                    </span>
                  </div>
                  <p className="text-sm text-slate-700 dark:text-slate-300">{segment.text}</p>
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
