import type { Dispatch, SetStateAction } from 'react'

interface SettingsProps {
  userId: string
  setUserId: Dispatch<SetStateAction<string>>
}

const Settings = ({ userId, setUserId }: SettingsProps) => {
  return (
    <div className="bg-gray-800 rounded-xl border border-gray-700 p-6">
      <h2 className="text-xl font-bold mb-4">Settings</h2>
      <div>
        <label className="block text-sm font-medium text-gray-400 mb-2">User ID</label>
        <input
          type="text"
          value={userId}
          onChange={(e) => setUserId(e.target.value)}
          className="w-full bg-gray-700 rounded-lg py-2 px-4 focus:outline-none focus:ring-2 focus:ring-primary-500"
        />
      </div>
    </div>
  )
}

export default Settings