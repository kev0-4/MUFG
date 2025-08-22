"use client"
import { useState } from "react"
import type React from "react"

import { useStockData } from "@/hooks/useApi"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export default function StockDataForm() {
  const [ticker, setTicker] = useState("AAPL")
  const [startDate, setStartDate] = useState("2024-01-01")
  const [endDate, setEndDate] = useState("2024-12-31")
  const { run, loading, error, data } = useStockData()

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    await run({ ticker, start_date: startDate, end_date: endDate })
  }

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>Historical Stock Data</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={onSubmit} className="grid grid-cols-3 gap-3">
          <div>
            <label className="text-sm">Stock Ticker</label>
            <Input value={ticker} onChange={(e) => setTicker(e.target.value.toUpperCase())} placeholder="AAPL" />
          </div>
          <div>
            <label className="text-sm">Start Date</label>
            <Input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} />
          </div>
          <div>
            <label className="text-sm">End Date</label>
            <Input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} />
          </div>
          <Button className="col-span-3" disabled={loading} type="submit">
            Get Data
          </Button>
        </form>
        {error && <pre className="mt-3 text-red-600 text-xs whitespace-pre-wrap">{error}</pre>}
        {data && <pre className="mt-3 bg-muted p-3 rounded text-xs overflow-auto">{JSON.stringify(data, null, 2)}</pre>}
      </CardContent>
    </Card>
  )
}
