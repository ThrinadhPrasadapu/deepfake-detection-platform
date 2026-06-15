"use client"

import { useState } from "react"
import { Navigation } from "@/components/navigation"
import { FileUpload } from "@/components/file-upload"
import { AnalysisResult, type AnalysisResult as AnalysisResultType } from "@/components/analysis-result"
import { Button } from "@/components/ui/button"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Loader2, VideoIcon, AlertCircle } from "lucide-react"

export default function VideoDetectionPage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [analyzing, setAnalyzing] = useState(false)
  const [result, setResult] = useState<AnalysisResultType | null>(null)
  const [progress, setProgress] = useState(0)
  const [error, setError] = useState<string | null>(null)

  const handleAnalyze = async () => {
    if (!selectedFile) return

    setAnalyzing(true)
    setResult(null)
    setError(null)
    setProgress(0)

    const progressInterval = setInterval(() => {
      setProgress((prev) => Math.min(prev + 3, 88))
    }, 400)

    try {
      const formData = new FormData()
      formData.append("file", selectedFile)

      const response = await fetch("/api/detect/video", { method: "POST", body: formData })
      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error ?? "Analysis failed")
      }

      setProgress(100)
      setResult(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unexpected error")
    } finally {
      clearInterval(progressInterval)
      setAnalyzing(false)
    }
  }

  const handleClearFile = () => {
    setSelectedFile(null)
    setResult(null)
    setProgress(0)
    setError(null)
  }

  return (
    <div className="min-h-screen bg-background relative overflow-hidden">
      <div className="fixed inset-0 -z-10">
        <div className="absolute inset-0 bg-gradient-to-br from-chart-2/8 via-background to-accent/8" />
        <div className="absolute top-0 left-1/2 w-96 h-96 bg-chart-2/6 rounded-full blur-3xl animate-pulse-slow" />
        <div className="absolute bottom-1/4 right-1/3 w-64 h-64 bg-accent/5 rounded-full blur-3xl animate-pulse-slow" style={{animationDelay:"1s"}} />
      </div>

      <Navigation />

      <main className="container mx-auto px-4 py-8 relative z-10">
        <div className="mb-8 animate-fade-in">
          <div className="flex items-center gap-3 mb-4">
            <div className="h-12 w-12 rounded-lg bg-chart-2/10 flex items-center justify-center animate-pulse-slow">
              <VideoIcon className="h-6 w-6 text-chart-2" />
            </div>
            <div>
              <h1 className="text-3xl font-bold">Video Detection</h1>
              <p className="text-muted-foreground">Frame-by-frame ResNet50 scoring with timeline visualization</p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="space-y-6 animate-slide-up">
            <div>
              <h2 className="text-xl font-semibold mb-4">Upload Video</h2>
              <FileUpload
                accept={{ "video/*": [".mp4", ".mov", ".avi", ".webm"] }}
                onFileSelect={setSelectedFile}
                selectedFile={selectedFile}
                onClearFile={handleClearFile}
                maxSize={52428800}
              />
            </div>

            {selectedFile && !analyzing && !result && (
              <Button onClick={handleAnalyze} className="w-full transition-all hover:scale-105" size="lg">
                Analyze Video
              </Button>
            )}

            {analyzing && (
              <div className="space-y-4 p-8 bg-card/50 backdrop-blur-sm rounded-lg border border-border animate-fade-in">
                <div className="flex items-center justify-center gap-3">
                  <Loader2 className="h-5 w-5 animate-spin text-chart-2" />
                  <span className="text-sm font-medium">Extracting frames + scoring…</span>
                </div>
                <div className="space-y-2">
                  <div className="h-2 bg-secondary rounded-full overflow-hidden">
                    <div
                      className="h-full bg-chart-2 transition-all duration-300 ease-out"
                      style={{ width: `${progress}%` }}
                    />
                  </div>
                  <p className="text-xs text-muted-foreground text-center">{progress}% complete</p>
                </div>
              </div>
            )}

            {error && (
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}
          </div>

          <div className="animate-slide-up" style={{ animationDelay: "0.1s" }}>
            {result && selectedFile && (
              <div>
                <h2 className="text-xl font-semibold mb-4">Results</h2>
                <AnalysisResult result={result} fileName={selectedFile.name} />
                <Button
                  onClick={handleClearFile}
                  variant="outline"
                  className="w-full mt-6 bg-transparent hover:bg-secondary transition-all"
                >
                  Analyze Another Video
                </Button>
              </div>
            )}

            {!result && !analyzing && !error && (
              <div className="p-8 bg-card/50 backdrop-blur-sm rounded-lg border border-border">
                <h2 className="text-xl font-semibold mb-4">About Video Detection</h2>
                <div className="space-y-4 text-sm text-muted-foreground">
                  <p>Pipeline: Frame extraction (OpenCV) → Face crop → ResNet50 per frame → Timeline</p>
                  <ul className="list-disc list-inside space-y-2 ml-2">
                    <li>Samples up to 20 frames evenly across the video</li>
                    <li>Per-frame fake score (0–100%) with timeline chart</li>
                    <li>Highlights exactly which seconds are suspicious</li>
                    <li>Temporal coherence via average + peak analysis</li>
                  </ul>
                  <p className="pt-2">
                    Supported formats: MP4, MOV, AVI, WEBM
                    <br />
                    Maximum file size: 50 MB
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}
