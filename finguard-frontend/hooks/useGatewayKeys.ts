"use client"
import { useEffect, useState } from "react"
import { loadGatewayPublicKey, loadClientPrivateKey } from "@/lib/crypto/gatewayCrypto"

export function useGatewayKeys() {
  const [ready, setReady] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    ;(async () => {
      try {
        await Promise.all([loadGatewayPublicKey(), loadClientPrivateKey()])
        setReady(true)
      } catch (e: any) {
        setError(e?.message ?? String(e))
      }
    })()
  }, [])

  return { ready, error }
}
