import SentimentsForm from "@/components/forms/SentimentsForm"
import EnhanceForm from "@/components/forms/EnhanceForm"
import QueryForm from "@/components/forms/QueryForm"

export default function NLP() {
  return (
    <main className="space-y-6">
      <SentimentsForm />
      <EnhanceForm />
      <QueryForm />
    </main>
  )
}
