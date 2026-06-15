import { Navigation } from "@/components/navigation"
import { DetectionCard } from "@/components/detection-card"
import { ImageIcon, VideoIcon, AudioLines, Shield, CheckCircle2, FileSearch } from "lucide-react"

export default function HomePage() {
  return (
    <div className="min-h-screen bg-background relative overflow-hidden">
      {/* Updated background with blue tech gradient and grid pattern */}
      <div className="fixed inset-0 -z-10">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/10 via-background to-accent/10" />
        <div
          className="absolute inset-0 opacity-10"
          style={{
            backgroundImage: `
              linear-gradient(oklch(0.65 0.25 230 / 0.1) 1px, transparent 1px),
              linear-gradient(90deg, oklch(0.65 0.25 230 / 0.1) 1px, transparent 1px)
            `,
            backgroundSize: "50px 50px",
          }}
        />
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-primary/5 rounded-full blur-3xl animate-pulse-slow" />
        <div
          className="absolute bottom-0 right-1/4 w-96 h-96 bg-accent/5 rounded-full blur-3xl animate-pulse-slow"
          style={{ animationDelay: "1s" }}
        />
      </div>

      <Navigation />

      <main className="container mx-auto px-4 py-8 relative z-10">
        {/* Updated hero section with presentation-style branding */}
        <div className="mb-16 animate-fade-in text-center">
          <div className="inline-flex items-center gap-3 mb-6 px-4 py-2 bg-primary/10 border border-primary/20 rounded-full">
            <Shield className="h-5 w-5 text-primary" />
            <span className="text-sm font-semibold text-primary">Agentic AI for Deepfake Detection</span>
          </div>
          <h1 className="text-5xl md:text-7xl font-bold mb-6 text-balance">
            <span className="bg-gradient-to-r from-primary via-accent to-primary bg-clip-text text-transparent">
              KYROS
            </span>
          </h1>
          <p className="text-2xl md:text-3xl font-semibold mb-4 text-foreground/90">Authenticity Verification System</p>
          <p className="text-lg text-muted-foreground max-w-3xl mx-auto text-pretty">
            Offline-first field agent for detecting deepfakes with tamper-proof evidence and signed reports. Real-time
            verification with explainable AI.
          </p>
        </div>

        {/* Added features section matching presentation key points */}
        <div className="mb-12 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div
            className="p-6 bg-card/50 backdrop-blur-sm border border-border rounded-lg animate-slide-up"
            style={{ animationDelay: "0.1s" }}
          >
            <div className="h-12 w-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
              <CheckCircle2 className="h-6 w-6 text-primary" />
            </div>
            <h3 className="text-lg font-semibold mb-2">Evidence-Based Output</h3>
            <p className="text-sm text-muted-foreground">
              Produces clear, explainable evidence with heatmaps, key frames, and confidence scoring instead of just
              labels
            </p>
          </div>
          <div
            className="p-6 bg-card/50 backdrop-blur-sm border border-border rounded-lg animate-slide-up"
            style={{ animationDelay: "0.2s" }}
          >
            <div className="h-12 w-12 bg-accent/10 rounded-lg flex items-center justify-center mb-4">
              <FileSearch className="h-6 w-6 text-accent" />
            </div>
            <h3 className="text-lg font-semibold mb-2">Multi-Agent Analysis</h3>
            <p className="text-sm text-muted-foreground">
              Automatically chooses the right forensic checks based on content type through parallel agent collaboration
            </p>
          </div>
          <div
            className="p-6 bg-card/50 backdrop-blur-sm border border-border rounded-lg animate-slide-up"
            style={{ animationDelay: "0.3s" }}
          >
            <div className="h-12 w-12 bg-chart-2/10 rounded-lg flex items-center justify-center mb-4">
              <Shield className="h-6 w-6 text-chart-2" />
            </div>
            <h3 className="text-lg font-semibold mb-2">Offline-First Detection</h3>
            <p className="text-sm text-muted-foreground">
              Works fully offline on devices for instant field verification with tamper-proof evidence generation
            </p>
          </div>
        </div>

        {/* Detection Methods */}
        <div>
          <h2 className="text-2xl font-bold mb-6">Choose Detection Method</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="animate-slide-up" style={{ animationDelay: "0.4s" }}>
              <DetectionCard
                title="Image Detection"
                description="Analyze images for AI-generated or manipulated content using CNN models"
                icon={ImageIcon}
                href="/detect/image"
                color="bg-primary/10 text-primary"
              />
            </div>
            <div className="animate-slide-up" style={{ animationDelay: "0.5s" }}>
              <DetectionCard
                title="Video Detection"
                description="Detect deepfake videos with frame-by-frame analysis and temporal modeling"
                icon={VideoIcon}
                href="/detect/video"
                color="bg-chart-2/10 text-chart-2"
              />
            </div>
            <div className="animate-slide-up" style={{ animationDelay: "0.6s" }}>
              <DetectionCard
                title="Audio Detection"
                description="Identify synthetic or cloned voices using spectrogram analysis"
                icon={AudioLines}
                href="/detect/audio"
                color="bg-chart-3/10 text-chart-3"
              />
            </div>
          </div>
        </div>

        {/* Info Section */}
        <div
          className="mt-12 p-8 bg-card/50 backdrop-blur-sm border border-primary/20 rounded-lg animate-fade-in relative overflow-hidden"
          style={{ animationDelay: "0.7s" }}
        >
          <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-primary via-accent to-primary opacity-50" />
          <h3 className="text-2xl font-bold mb-6 flex items-center gap-2">
            <Shield className="h-6 w-6 text-primary" />
            Detection Pipeline
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 text-sm">
            <div className="relative">
              <div className="h-12 w-12 bg-primary/10 rounded-lg flex items-center justify-center mb-3 animate-glow">
                <span className="text-xl font-bold text-primary">1</span>
              </div>
              <h4 className="text-foreground font-semibold mb-2">Media Input</h4>
              <p className="text-muted-foreground">Upload image, video, or audio for analysis</p>
            </div>
            <div className="relative">
              <div className="h-12 w-12 bg-accent/10 rounded-lg flex items-center justify-center mb-3">
                <span className="text-xl font-bold text-accent">2</span>
              </div>
              <h4 className="text-foreground font-semibold mb-2">Parallel Analysis</h4>
              <p className="text-muted-foreground">Multiple forensic agents process content simultaneously</p>
            </div>
            <div className="relative">
              <div className="h-12 w-12 bg-primary/10 border border-primary/20 rounded-lg flex items-center justify-center mb-3 animate-glow">
                <span className="text-xl font-bold text-primary">3</span>
              </div>
              <h4 className="text-foreground font-semibold mb-2">Confidence Scoring</h4>
              <p className="text-muted-foreground">Agent collaboration generates authenticity scores</p>
            </div>
            <div className="relative">
              <div className="h-12 w-12 bg-primary/10 border border-primary/20 rounded-lg flex items-center justify-center mb-3 animate-glow">
                <span className="text-xl font-bold text-primary">4</span>
              </div>
              <h4 className="text-foreground font-semibold mb-2">Final Output</h4>
              <p className="text-muted-foreground">Real/Fake/Suspicious with detailed evidence</p>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
