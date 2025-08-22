import UserDataForm from "@/components/forms/UserDataForm"
import SimulateForm from "@/components/forms/SimulateForm"
import RecommendForm from "@/components/forms/RecommendForm"

export default function Dashboard() {
  return (
    <main className="space-y-6">
      <UserDataForm />
      <SimulateForm />
      <RecommendForm />
    </main>
  )
}
