"use client"
import { useGatewayKeys } from "@/hooks/useGatewayKeys"
import { Badge } from "@/components/ui/badge"

export default function KeyStatus() {
  const { ready, error } = useGatewayKeys()
  if (error) return <Badge variant="destructive">Key error: {error}</Badge>
  return <Badge variant={ready ? "default" : "secondary"}>{ready ? "Crypto ready" : "Loading keys..."}</Badge>
}
