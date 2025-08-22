import type { Dispatch, SetStateAction } from 'react'
import type { PortfolioData, UserData } from '../types'

interface PortfolioProps {
  userId: string
  portfolioData: PortfolioData | null
  response: UserData | null
  setPortfolioData: Dispatch<SetStateAction<PortfolioData | null>>
  callEndpoint: (endpoint: string, method: string, data?: any) => Promise<any>
}

const Portfolio = ({ userId, portfolioData, response, setPortfolioData, callEndpoint }: PortfolioProps) => {
  const fetchPortfolio = async () => {
    const data = await callEndpoint('portfolio', 'POST')
    if (data) setPortfolioData(data)
  }

  return (
    <div className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
      <div className="p-6 border-b border-gray-700">
        <h2 className="text-xl font-bold mb-1">Portfolio Summary</h2>
        <p className="text-gray-400 text-sm">Current holdings and performance</p>
      </div>
      <div className="p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-gray-700/50 p-4 rounded-lg">
            <p className="text-gray-400 text-sm mb-1">Total Value</p>
            <p className="text-2xl font-bold">${portfolioData?.portfolio?.totalValue?.toFixed(2) || 'Click to fetch'}</p>
            <button onClick={fetchPortfolio} className="text-primary-400 hover:text-primary-300 text-sm flex items-center mt-1">
              Refresh
              <span className="material-symbols-outlined ml-1">refresh</span>
            </button>
          </div>
          <div className="bg-gray-700/50 p-4 rounded-lg">
            <p className="text-gray-400 text-sm mb-1">Superannuation</p>
            <p className="text-2xl font-bold">${response?.super_balance?.toFixed(2) || 'Click to fetch'}</p>
            <button
              onClick={() => callEndpoint('user-data', 'POST', { user_id: userId })}
              className="text-primary-400 hover:text-primary-300 text-sm flex items-center mt-1"
            >
              Refresh
              <span className="material-symbols-outlined ml-1">refresh</span>
            </button>
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-gray-400 border-b border-gray-700">
                <th className="text-left pb-3 font-medium">Asset</th>
                <th className="text-left pb-3 font-medium">Type</th>
                <th className="text-right pb-3 font-medium">Quantity</th>
                <th className="text-right pb-3 font-medium">Avg. Price</th>
                <th className="text-right pb-3 font-medium">Current</th>
                <th className="text-right pb-3 font-medium">P/L</th>
              </tr>
            </thead>
            <tbody>
              {portfolioData?.holdings?.map((holding, i) => (
                <tr key={i} className="border-b border-gray-700 hover:bg-gray-700/30 transition-colors">
                  <td className="py-3 flex items-center">
                    <div className="w-8 h-8 rounded-full bg-blue-500/20 flex items-center justify-center mr-2">
                      <span className="font-semibold text-blue-400">{holding.symbol}</span>
                    </div>
                    {holding.symbol}
                  </td>
                  <td className="py-3">{holding.assetType}</td>
                  <td className="py-3 text-right">{holding.quantity}</td>
                  <td className="py-3 text-right">${holding.purchasePrice?.toFixed(2)}</td>
                  <td className="py-3 text-right font-medium">${holding.currentPrice?.toFixed(2)}</td>
                  <td className="py-3 text-right">
                    <span className={((holding.currentPrice - holding.purchasePrice) / holding.purchasePrice * 100) > 0 ? 'text-emerald-500' : 'text-rose-500'}>
                      {(((holding.currentPrice - holding.purchasePrice) / holding.purchasePrice * 100).toFixed(2))}%
                    </span>
                  </td>
                </tr>
              )) || (
                <tr>
                  <td colSpan={6} className="py-3 text-center">
                    Click Refresh to load holdings
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

export default Portfolio