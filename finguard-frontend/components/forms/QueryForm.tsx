"use client"
import { useState } from "react"
import type React from "react"

import { useQuery } from "@/hooks/useApi"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export default function QueryForm() {
  const [userId, setUserId] = useState("uid1")
  const [query, setQuery] = useState("What are my investment options?")
  const { run, loading, error, data } = useQuery()

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    await run({ user_id: userId, query })
  }

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>Query System</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={onSubmit} className="space-y-3">
          <div>
            <label className="text-sm">User ID</label>
            <Input value={userId} onChange={(e) => setUserId(e.target.value)} placeholder="uid1" />
          </div>
          <div>
            <label className="text-sm">Query</label>
            <Textarea value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Enter your query..." />
          </div>
          <Button disabled={loading} type="submit" className="w-full">
            Submit Query
          </Button>
        </form>
        {error && <pre className="mt-3 text-red-600 text-xs whitespace-pre-wrap">{error}</pre>}
        {data && <pre className="mt-3 bg-muted p-3 rounded text-xs overflow-auto">{JSON.stringify(data, null, 2)}</pre>}
      </CardContent>
    </Card>
  )
}
