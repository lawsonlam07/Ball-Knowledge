"use client"

import { useEffect, useState } from "react"
import Image from "next/image"

export default function LoadingPage() {
  const [progress, setProgress] = useState(0)
  const [currentStep, setCurrentStep] = useState("Uploading video...")

  const steps = [
    "Uploading video...",
    "Processing video frames...",
    "Analyzing tennis gameplay...",
    "Detecting players and ball...",
    "Identifying key moments...",
    "Generating AI commentary...",
    "Finalizing your experience..."
  ]

  useEffect(() => {
    // Simulate progress
    const progressInterval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 100) {
          clearInterval(progressInterval)
          // TODO: Navigate to viewer page
          return 100
        }
        return prev + 1
      })
    }, 200)

    // Update step based on progress
    const stepInterval = setInterval(() => {
      setProgress((prev) => {
        const stepIndex = Math.floor((prev / 100) * steps.length)
        if (stepIndex < steps.length) {
          setCurrentStep(steps[stepIndex])
        }
        return prev
      })
    }, 500)

    return () => {
      clearInterval(progressInterval)
      clearInterval(stepInterval)
    }
  }, [])

  return (
    <div className="min-h-screen bg-linear-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800 p-6 flex items-center justify-center">
      <div className="w-full max-w-md">
        {/* Bouncing Tennis Ball Animation */}
        <div className="flex justify-center h-32 relative items-end">
          <style jsx>{`
            @keyframes bounce {
              0%, 100% {
                transform: translateY(0);
                animation-timing-function: cubic-bezier(0, 0, 0.2, 1);
              }
              50% {
                transform: translateY(-80px);
                animation-timing-function: cubic-bezier(0.8, 0, 1, 1);
              }
            }
            .bounce-animation {
              animation: bounce 1s infinite;
            }
          `}</style>
          <div className="bounce-animation">
            <Image
              src="/tennis-ball.svg"
              alt="Loading"
              width={80}
              height={80}
            />
          </div>
        </div>

        {/* Progress Bar */}
        <div className="space-y-3">
          <div className="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-2 overflow-hidden">
            <div
              className="bg-primary h-full transition-all duration-300 ease-out rounded-full"
              style={{ width: `${progress}%` }}
            />
          </div>
          <p className="text-center text-base font-medium text-slate-700 dark:text-slate-300">
            {currentStep}
          </p>
        </div>
      </div>
    </div>
  )
}
