import StockLatestForm from "@/components/forms/StockLatestForm"
import StockDataForm from "@/components/forms/StockDataForm"

export default function Stocks() {
  return (
    <main className="space-y-6">
      <StockLatestForm />
      <StockDataForm />
    </main>
  )
}
