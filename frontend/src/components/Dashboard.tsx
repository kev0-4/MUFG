import { useEffect } from 'react'
import { Line } from 'react-chartjs-2'
import { Chart as ChartJS, LineElement, PointElement, LinearScale, TimeScale, Title, Tooltip, Legend } from 'chart.js'
import type { YFinanceData, StockLatest, StockData } from '../types'

ChartJS.register(LineElement, PointElement, LinearScale, TimeScale, Title, Tooltip, Legend)

interface DashboardProps {
  marketData: { [key: string]: YFinanceData }
  intcData: StockLatest | null
  aaplData: StockLatest | null
  stockData: StockData | null
  ticker: string
  setTicker: (ticker: string) => void
  callEndpoint: (endpoint: string, method: string, data?: any) => Promise<any>
  setStockData: (data: StockData | null) => void
}

const Dashboard = ({ marketData, intcData, aaplData, stockData, ticker, setTicker, callEndpoint, setStockData }: DashboardProps) => {
  const fetchStockData = async () => {
    const today = new Date('2025-08-22')
    const thirtyDaysAgo = new Date(today)
    thirtyDaysAgo.setDate(today.getDate() - 30)
    const data = await callEndpoint('stock-data', 'POST', {
      ticker,
      start_date: thirtyDaysAgo.toISOString().split('T')[0],
      end_date: today.toISOString().split('T')[0],
    })
    if (data) setStockData(data)
  }

  useEffect(() => {
    if (stockData) {
      // Chart is rendered via react-chartjs-2
    }
  }, [stockData])

  const chartData = stockData
    ? {
        labels: stockData.prices.map((p) => p.date),
        datasets: [
          {
            label: ticker,
            data: stockData.prices.map((p) => parseFloat(p.close)),
            borderColor: '#7341ff',
            fill: false,
          },
        ],
      }
    : null

  return (
    <div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
        {Object.entries(marketData).map(([ticker, data]) => (
          <div key={ticker} className="bg-gray-800 rounded-xl p-4 border border-gray-700 hover:border-primary-500 transition-colors">
            <div className="flex justify-between items-start mb-4">
              <div>
                <p className="text-gray-400 text-sm">
                  {ticker === '^GSPC' ? 'S&P 500' : ticker === '^IXIC' ? 'NASDAQ' : ticker === '^DJI' ? 'Dow Jones' : 'US 10Y Bond'}
                </p>
                <h3 className="text-2xl font-bold">{data.value}{ticker === '^TNX' ? '%' : ''}</h3>
              </div>
              <span className={`flex items-center text-sm font-semibold ${data.change.startsWith('+') ? 'text-emerald-500' : 'text-rose-500'}`}>
                {data.change}
                <span className="material-symbols-outlined ml-1 text-base">
                  {data.change.startsWith('+') ? 'trending_up' : 'trending_down'}
                </span>
              </span>
            </div>
            <div className={`h-12 w-full bg-gradient-to-r ${data.change.startsWith('+') ? 'from-emerald-500/10 to-emerald-500/5' : 'from-rose-500/10 to-rose-500/5'} rounded`}>
              <div className="h-full w-full flex items-end">
                {Array(12)
                  .fill(0)
                  .map((_, i) => (
                    <div
                      key={i}
                      className={`h-${Math.floor(Math.random() * 8 + 3)} w-1/12 ${data.change.startsWith('+') ? 'bg-emerald-500' : 'bg-rose-500'} rounded-sm mx-px`}
                    ></div>
                  ))}
              </div>
            </div>
          </div>
        ))}
        <div className="bg-gray-800 rounded-xl p-4 border border-gray-700 hover:border-primary-500 transition-colors">
          <button onClick={() => callEndpoint('stock-latest/INTC', 'GET')} className="w-full text-left">
            <div className="flex justify-between items-start mb-4">
              <div>
                <p className="text-gray-400 text-sm">INTC Latest</p>
                <h3 className="text-2xl font-bold">{intcData?.latest_price?.close || 'Click to fetch'}</h3>
              </div>
              <span className="text-emerald-500 flex items-center text-sm font-semibold">
                {intcData?.latest_price?.volume || '-'} Vol
              </span>
            </div>
          </button>
        </div>
        <div className="bg-gray-800 rounded-xl p-4 border border-gray-700 hover:border-primary-500 transition-colors">
          <button onClick={() => callEndpoint('stock-latest/AAPL', 'GET')} className="w-full text-left">
            <div className="flex justify-between items-start mb-4">
              <div>
                <p className="text-gray-400 text-sm">AAPL Latest</p>
                <h3 className="text-2xl font-bold">{aaplData?.latest_price?.close || 'Click to fetch'}</h3>
              </div>
              <span className="text-emerald-500 flex items-center text-sm font-semibold">
                {aaplData?.latest_price?.volume || '-'} Vol
              </span>
            </div>
          </button>
        </div>
      </div>
      <div className="bg-gray-800 rounded-xl p-6 border border-gray-700 mb-6">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h2 className="text-xl font-bold">Market Trends</h2>
            <p className="text-gray-400 text-sm">Historical performance of {ticker}</p>
          </div>
          <div className="flex space-x-2">
            <div className="relative">
              <input
                type="text"
                value={ticker}
                onChange={(e) => setTicker(e.target.value)}
                className="bg-gray-700 text-sm rounded-lg px-4 py-2 w-32 focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
            <button
              onClick={fetchStockData}
              className="bg-primary-500 hover:bg-primary-600 text-white px-4 py-2 rounded-lg text-sm transition-colors flex items-center"
            >
              <span className="material-symbols-outlined mr-1 text-base">refresh</span>
              Update
            </button>
          </div>
        </div>
        <div className="h-80 w-full relative">
          {stockData ? (
            <Line data={chartData!} options={{ scales: { x: { type: 'time', time: { unit: 'day' } }, y: { beginAtZero: false } } }} />
          ) : (
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-gray-500 text-center">
                <span className="material-symbols-outlined text-6xl">candlestick_chart</span>
                <p className="mt-2">Click Update to fetch data</p>
                <p className="text-sm text-gray-400">Using: /api/stock-data</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Dashboard