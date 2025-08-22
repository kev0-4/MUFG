import type { Dispatch, SetStateAction } from "react";

interface SidebarProps {
  activeTab: string;
  setActiveTab: Dispatch<SetStateAction<string>>;
}

const Sidebar = ({ activeTab, setActiveTab }: SidebarProps) => {
  const navItems = [
    { id: "Dashboard", icon: "dashboard", label: "Dashboard" },
    { id: "AI Assistant", icon: "chat", label: "AI Assistant" },
    { id: "Portfolio", icon: "account_balance", label: "Portfolio" },
    { id: "Simulation", icon: "trending_up", label: "Simulation" },
    { id: "Insights", icon: "insights", label: "Insights" },
    { id: "Profile", icon: "person", label: "Profile" },
    { id: "Settings", icon: "settings", label: "Settings" },
  ];

  return (
    <div className="w-64 bg-gray-800 border-r border-gray-700 flex flex-col">
      <div className="p-4 border-b border-gray-700 flex items-center space-x-2">
        <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-emerald-600 rounded-lg flex items-center justify-center">
          <span className="material-symbols-outlined text-xl">security</span>
        </div>
        <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary-500 to-emerald-400">
          FinGuard
        </h1>
      </div>
      <nav className="flex-1 pt-4">
        <div className="px-4 mb-3 text-xs font-semibold text-gray-400 uppercase tracking-wider">
          Main
        </div>
        {navItems.slice(0, 5).map((item) => (
          <a
            key={item.id}
            href="#"
            className={`flex items-center px-4 py-3 text-gray-400 hover:bg-gray-700 hover:text-white transition-colors rounded-lg mx-2 ${
              activeTab === item.id ? "bg-gray-700 text-white" : ""
            }`}
            onClick={() => setActiveTab(item.id)}
          >
            <span className="material-symbols-outlined mr-3">{item.icon}</span>{" "}
            {item.label}
          </a>
        ))}
        <div className="px-4 mt-6 mb-3 text-xs font-semibold text-gray-400 uppercase tracking-wider">
          Account
        </div>
        {navItems.slice(5).map((item) => (
          <a
            key={item.id}
            href="#"
            className={`flex items-center px-4 py-3 text-gray-400 hover:bg-gray-700 hover:text-white transition-colors rounded-lg mx-2 ${
              activeTab === item.id ? "bg-gray-700 text-white" : ""
            }`}
            onClick={() => setActiveTab(item.id)}
          >
            <span className="material-symbols-outlined mr-3">{item.icon}</span>{" "}
            {item.label}
          </a>
        ))}
      </nav>
      <div className="p-4 border-t border-gray-700">
        <div className="flex items-center">
          <img
            src="https://images.unsplash.com/photo-1633332755192-727a05c4013d?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3MzkyNDZ8MHwxfHNlYXJjaHwxfHx1c2VyJTIwYXZhdGFyfGVufDB8fHx8MTc1NTgzODc1Mnww&ixlib=rb-4.1.0&q=80&w=1080"
            alt="User avatar"
            className="w-8 h-8 rounded-full mr-3"
          />
          <div>
            <p className="text-sm font-medium">Alex Morgan</p>
            <p className="text-xs text-gray-400">Premium Plan</p>
          </div>
          <button className="ml-auto text-gray-400 hover:text-white transition-colors">
            <span className="material-symbols-outlined">logout</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
