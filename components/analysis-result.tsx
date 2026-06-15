import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { AlertTriangle, CheckCircle, Info } from "lucide-react"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"

export interface AnalysisResult {
  isDeepfake: boolean
  confidence: number
  processingTime: number
  details: { label: string; value: string }[]
  // XAI visualizations (optional — populated by backend)
  gradcamImage?: string    // base64 PNG: original | heatmap | overlay (image detection)
  spectrogramImage?: string // base64 PNG: mel-spectrogram (audio detection)
  timelineImage?: string   // base64 PNG: per-frame fake score chart (video detection)
  frameTimeline?: { frame: number; timestamp: number; fakeScore: number }[]
}

interface AnalysisResultProps {
  result: AnalysisResult
  fileName: string
}

export function AnalysisResult({ result, fileName }: AnalysisResultProps) {
  const Icon = result.isDeepfake ? AlertTriangle : CheckCircle
  const statusColor = result.isDeepfake ? "text-destructive" : "text-accent"
  const statusBg = result.isDeepfake ? "bg-destructive/10" : "bg-accent/10"

  const visualizationImage = result.gradcamImage ?? result.spectrogramImage ?? result.timelineImage
  const visualizationLabel = result.gradcamImage
    ? "GradCAM Explainability — Original | Heatmap | Overlay"
    : result.spectrogramImage
    ? "Mel-Spectrogram Analysis"
    : result.timelineImage
    ? "Frame-level Fake Score Timeline"
    : null

  return (
    <div className="space-y-6">
      <Alert className={`${statusBg} border-${result.isDeepfake ? "destructive" : "accent"}`}>
        <Icon className={`h-4 w-4 ${statusColor}`} />
        <AlertTitle className={statusColor}>
          {result.isDeepfake ? "Deepfake Detected" : "Content Appears Authentic"}
        </AlertTitle>
        <AlertDescription>
          {result.isDeepfake
            ? "This content shows signs of AI manipulation or generation"
            : "No significant manipulation detected in this content"}
        </AlertDescription>
      </Alert>

      <Card className="bg-card border-border">
        <CardHeader>
          <CardTitle>Analysis Results</CardTitle>
          <CardDescription>File: {fileName}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium">Confidence Score</span>
              <span className="text-2xl font-bold">{result.confidence}%</span>
            </div>
            <Progress value={result.confidence} className="h-2" />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {result.details.map((detail, index) => (
              <div key={index} className="p-4 bg-secondary rounded-lg">
                <p className="text-sm text-muted-foreground">{detail.label}</p>
                <p className="font-semibold mt-1">{detail.value}</p>
              </div>
            ))}
          </div>

          {/* XAI Visualization */}
          {visualizationImage && (
            <div className="pt-2">
              <p className="text-sm font-medium text-muted-foreground mb-3">{visualizationLabel}</p>
              <div className="rounded-lg overflow-hidden border border-border">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={visualizationImage}
                  alt={visualizationLabel ?? "Visualization"}
                  className="w-full h-auto"
                />
              </div>
            </div>
          )}

          <div className="pt-4 border-t border-border">
            <div className="flex items-start gap-2">
              <Info className="h-4 w-4 text-muted-foreground mt-0.5 shrink-0" />
              <p className="text-xs text-muted-foreground">
                Analysis performed by KYROS using ResNet50 + GradCAM XAI. Results are guidance only —
                verify with additional sources for critical decisions. Processing time:{" "}
                {result.processingTime}s.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
