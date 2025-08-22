import type { Dispatch, SetStateAction } from 'react'
import type { SimulationData } from '../types'

interface SimulationProps {
  userId: string
  amount: string
  setAmount: Dispatch<SetStateAction<string>>
  stocks: string
  setStocks: Dispatch<SetStateAction<string>>
  aiPrompt: string
  setAiPrompt: Dispatch<SetStateAction<string>>
  response: SimulationData | null
  callEndpoint: (endpoint: string, method: string, data?: any) => Promise<any>
}

const Simulation = ({ userId, amount, setAmount, stocks, setStocks, aiPrompt, setAiPrompt, response, callEndpoint }: SimulationProps) => {
  return (
    <div className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
      <div className="p-6 border-b border-gray-700 flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold mb-1">Investment Simulator</h2>
          <p className="text-gray-400 text-sm">Project future returns based on different scenarios</p>
        </div>
        <button
          onClick={() =>
            callEndpoint('enhance', 'POST', {
              user_id: userId,
              simulation_data: { amount: parseFloat(amount), stocks: stocks.split(',') },
              ai_prompt: aiPrompt,
            })
          }
          className="bg-primary-500 hover:bg-primary-600 text-white px-4 py-2 rounded-lg text-sm transition-colors flex items-center"
        >
          <span className="material-symbols-outlined mr-1">rocket_launch</span>
          AI Enhance
        </button>
      </div>
      <div className="p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-2">Investment Amount</label>
            <div className="relative">
              <span className="absolute left-3 top-3 text-gray-400">$</span>
              <input
                type="text"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                className="w-full bg-gray-700 rounded-lg py-2 pl-8 pr-4 focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-2">Stock Ticker</label>
            <div className="relative">
              <input
                type="text"
                value={stocks}
                onChange={(e) => setStocks(e.target.value)}
                className="w-full bg-gray-700 rounded-lg py-2 px-4 focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
              <button
                onClick={() =>
                  callEndpoint('simulate', 'POST', {
                    user_id: userId,
                    simulation_data: { amount: parseFloat(amount), stocks: stocks.split(','), duration_months: 12 },
                  })
                }
                className="absolute right-2 top-2 text-gray-400 hover:text-white"
              >
                <span className="material-symbols-outlined">play_arrow</span>
              </button>
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-2">AI Prompt</label>
            <input
              type="text"
              value={aiPrompt}
              onChange={(e) => setAiPrompt(e.target.value)}
              className="w-full bg-gray-700 rounded-lg py-2 px-4 focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
        </div>
        {response?.projected_balance && (
          <div className="bg-gray-700/50 p-4 rounded-lg">
            <p className="text-lg font-bold">Projected Balance: ${response.projected_balance.toFixed(2)}</p>
            <p className="text-gray-400">{response.eli5_response}</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default Simulation