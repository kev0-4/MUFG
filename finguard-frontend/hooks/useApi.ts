"use client"
import { useState, useCallback } from "react"
import { api } from "@/lib/apiClient"

export function useApiAction<T extends any[]>(fn: (...args: T) => Promise<any>) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [data, setData] = useState<any>(null)

  const run = useCallback(
    async (...args: T) => {
      setLoading(true)
      setError(null)
      try {
        const result = await fn(...args)
        setData(result)
        return result
      } catch (e: any) {
        setError(e?.message ?? String(e))
        throw e
      } finally {
        setLoading(false)
      }
    },
    [fn],
  )

  return { run, loading, error, data, setData }
}

export function useUserData() {
  return useApiAction(api.userData)
}

export function useSimulate() {
  return useApiAction(api.simulate)
}

export function useRecommend() {
  return useApiAction(api.recommend)
}

export function useSentiments() {
  return useApiAction(api.sentiments)
}

export function useEnhance() {
  return useApiAction(api.enhance)
}

export function useQuery() {
  return useApiAction(api.query)
}

export function useStockLatest() {
  return useApiAction(api.stockLatest as any)
}

export function useStockData() {
  return useApiAction(api.stockData)
}
