"use client"
import { useState } from "react"
import type React from "react"

import { useStockLatest } from "@/hooks/useApi"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export default function StockLatestForm() {
  const [ticker, setTicker] = useState("INTC")
  const { run, loading, error, data } = useStockLatest()

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    await run(ticker)
  }

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>Latest Stock Data</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={onSubmit} className="flex gap-2 items-end">
          <div className="flex-1">
            <label className="text-sm">Stock Ticker</label>
            <Input value={ticker} onChange={(e) => setTicker(e.target.value.toUpperCase())} placeholder="INTC" />
          </div>
          <Button disabled={loading} type="submit">
            Get Latest
          </Button>
        </form>
        {error && <pre className="mt-3 text-red-600 text-xs whitespace-pre-wrap">{error}</pre>}
        {data && <pre className="mt-3 bg-muted p-3 rounded text-xs overflow-auto">{JSON.stringify(data, null, 2)}</pre>}
      </CardContent>
    </Card>
  )
}
