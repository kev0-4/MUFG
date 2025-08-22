import KeyStatus from "@/components/KeyStatus"
import { Button } from "@/components/ui/button"
import Link from "next/link"

export default function Home() {
  return (
    <main className="space-y-6">
      <div className="flex items-center gap-3">
        <KeyStatus />
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Link href="/dashboard">
          <Button className="w-full">Dashboard</Button>
        </Link>
        <Link href="/stocks">
          <Button className="w-full" variant="secondary">
            Stocks
          </Button>
        </Link>
        <Link href="/nlp">
          <Button className="w-full bg-transparent" variant="outline">
            NLP
          </Button>
        </Link>
      </div>
    </main>
  )
}
