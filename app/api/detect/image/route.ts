import { NextRequest, NextResponse } from "next/server"

const BACKEND = process.env.BACKEND_URL ?? "http://localhost:8001"

export async function POST(request: NextRequest) {
  const formData = await request.formData()

  let res: Response
  try {
    res = await fetch(`${BACKEND}/detect/image`, { method: "POST", body: formData })
  } catch {
    return NextResponse.json(
      { error: "Python backend unreachable. Start it with: cd backend && uvicorn main:app --reload" },
      { status: 503 },
    )
  }

  const data = await res.json()
  return NextResponse.json(data, { status: res.status })
}
