"use client"
import { useState } from "react"
import type React from "react"

import { useSimulate } from "@/hooks/useApi"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export default function SimulateForm() {
  const [userId, setUserId] = useState("uid1")
  const [timeframe, setTimeframe] = useState(10)
  const [projected, setProjected] = useState(360000.45)
  const { run, loading, error, data } = useSimulate()

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    await run({ user_id: userId, simulation_data: { timeframe, projected_balance: projected } })
  }

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>Simulate Investment</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={onSubmit} className="grid grid-cols-3 gap-3">
          <div className="col-span-1">
            <label className="text-sm">User ID</label>
            <Input value={userId} onChange={(e) => setUserId(e.target.value)} />
          </div>
          <div>
            <label className="text-sm">Timeframe (years)</label>
            <Input
              type="number"
              value={timeframe}
              onChange={(e) => setTimeframe(Number.parseInt(e.target.value || "0"))}
            />
          </div>
          <div>
            <label className="text-sm">Projected Balance</label>
            <Input
              type="number"
              step="0.01"
              value={projected}
              onChange={(e) => setProjected(Number.parseFloat(e.target.value || "0"))}
            />
          </div>
          <Button className="col-span-3" disabled={loading} type="submit">
            Run
          </Button>
        </form>
        {error && <pre className="mt-3 text-red-600 text-xs whitespace-pre-wrap">{error}</pre>}
        {data && <pre className="mt-3 bg-muted p-3 rounded text-xs overflow-auto">{JSON.stringify(data, null, 2)}</pre>}
      </CardContent>
    </Card>
  )
}
