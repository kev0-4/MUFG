interface TopBarProps {
  activeTab: string
}

const TopBar = ({ activeTab }: TopBarProps) => {
  return (
    <div className="h-16 bg-gray-800 border-b border-gray-700 flex items-center justify-between px-6">
      <div className="flex items-center">
        <button className="text-gray-400 hover:text-white mr-4">
          <span className="material-symbols-outlined">menu</span>
        </button>
        <h2 className="text-lg font-semibold">{activeTab}</h2>
      </div>
      <div className="flex items-center space-x-4">
        <div className="relative">
          <input
            type="text"
            placeholder="Search..."
            className="bg-gray-700 text-gray-200 px-4 py-2 rounded-full text-sm w-64 focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
          <span className="material-symbols-outlined absolute right-3 top-2 text-gray-400">search</span>
        </div>
        <button className="w-9 h-9 rounded-full flex items-center justify-center bg-gray-700 hover:bg-gray-600 transition-colors relative">
          <span className="material-symbols-outlined">notifications</span>
          <span className="absolute top-0 right-0 w-2 h-2 rounded-full bg-primary-500"></span>
        </button>
        <button className="w-9 h-9 rounded-full flex items-center justify-center bg-gray-700 hover:bg-gray-600 transition-colors">
          <span className="material-symbols-outlined">help_outline</span>
        </button>
      </div>
    </div>
  )
}

export default TopBar