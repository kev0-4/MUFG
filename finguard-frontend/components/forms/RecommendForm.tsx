"use client"
import { useState } from "react"
import type React from "react"

import { useRecommend } from "@/hooks/useApi"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export default function RecommendForm() {
  const [userId, setUserId] = useState("uid1")
  const { run, loading, error, data } = useRecommend()

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    await run({ user_id: userId })
  }

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>Get Recommendations</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={onSubmit} className="flex gap-2 items-end">
          <div className="flex-1">
            <label className="text-sm">User ID</label>
            <Input value={userId} onChange={(e) => setUserId(e.target.value)} placeholder="uid1" />
          </div>
          <Button disabled={loading} type="submit">
            Get Recommendations
          </Button>
        </form>
        {error && <pre className="mt-3 text-red-600 text-xs whitespace-pre-wrap">{error}</pre>}
        {data && <pre className="mt-3 bg-muted p-3 rounded text-xs overflow-auto">{JSON.stringify(data, null, 2)}</pre>}
      </CardContent>
    </Card>
  )
}
