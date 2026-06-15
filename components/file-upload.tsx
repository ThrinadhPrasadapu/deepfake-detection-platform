"use client"

import { useState, useCallback } from "react"
import { useDropzone } from "react-dropzone"
import { Upload, X, FileImage } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"

interface FileUploadProps {
  accept: Record<string, string[]>
  onFileSelect: (file: File) => void
  selectedFile: File | null
  onClearFile: () => void
  maxSize?: number
}

export function FileUpload({ accept, onFileSelect, selectedFile, onClearFile, maxSize = 10485760 }: FileUploadProps) {
  const [error, setError] = useState<string>("")

  const onDrop = useCallback(
    (acceptedFiles: File[], rejectedFiles: any[]) => {
      setError("")

      if (rejectedFiles.length > 0) {
        const rejection = rejectedFiles[0]
        if (rejection.errors[0]?.code === "file-too-large") {
          setError(`File is too large. Maximum size is ${maxSize / 1048576}MB`)
        } else if (rejection.errors[0]?.code === "file-invalid-type") {
          setError("Invalid file type. Please upload a supported format")
        } else {
          setError("File upload failed. Please try again")
        }
        return
      }

      if (acceptedFiles.length > 0) {
        onFileSelect(acceptedFiles[0])
      }
    },
    [onFileSelect, maxSize],
  )

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept,
    maxSize,
    multiple: false,
  })

  if (selectedFile) {
    return (
      <Card className="p-6 bg-card border-border">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center">
              <FileImage className="h-6 w-6 text-primary" />
            </div>
            <div>
              <p className="font-medium">{selectedFile.name}</p>
              <p className="text-sm text-muted-foreground">{(selectedFile.size / 1024).toFixed(2)} KB</p>
            </div>
          </div>
          <Button variant="ghost" size="icon" onClick={onClearFile}>
            <X className="h-4 w-4" />
          </Button>
        </div>
      </Card>
    )
  }

  return (
    <div>
      <Card
        {...getRootProps()}
        className={`p-12 border-2 border-dashed cursor-pointer transition-colors ${
          isDragActive
            ? "border-primary bg-primary/5"
            : error
              ? "border-destructive bg-destructive/5"
              : "border-border bg-card hover:border-primary/50"
        }`}
      >
        <input {...getInputProps()} />
        <div className="flex flex-col items-center justify-center gap-4 text-center">
          <div className="h-16 w-16 rounded-full bg-primary/10 flex items-center justify-center">
            <Upload className="h-8 w-8 text-primary" />
          </div>
          <div>
            <p className="text-lg font-medium">{isDragActive ? "Drop your file here" : "Drag & drop your file here"}</p>
            <p className="text-sm text-muted-foreground mt-1">or click to browse</p>
          </div>
          <p className="text-xs text-muted-foreground">Maximum file size: {maxSize / 1048576}MB</p>
        </div>
      </Card>
      {error && <p className="text-sm text-destructive mt-2">{error}</p>}
    </div>
  )
}
