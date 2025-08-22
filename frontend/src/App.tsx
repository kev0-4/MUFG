import { useState, useEffect } from 'react'
import Sidebar from './components/Sidebar'
import TopBar from './components/TopBar'
import Dashboard from './components/Dashboard'
import AIAssistant from './components/AIAssistant'
import Portfolio from './components/Portfolio'
import Simulation from './components/Simulation'
import Insights from './components/Insights'
import Profile from './components/Profile'
import type Settings from './components/Settings'
import type { YFinanceData, StockLatest, StockData, PortfolioData, UserData, SimulationData, QueryData, RecommendationData, SentimentData, KeyData, ChatMessage } from './types'

const API_GATEWAY_URL = 'http://20.244.41.104:8080'
const GEMINI_API_KEY = 'YOUR_GEMINI_API_KEY' // Replace with your Gemini API key
const GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent'

const App = () => {
  const [activeTab, setActiveTab] = useState('Dashboard')
  const [userId, setUserId] = useState('uid1')
  const [ticker, setTicker] = useState('AAPL')
  const [amount, setAmount] = useState('10000')
  const [stocks, setStocks] = useState('AAPL,GOOGL')
  const [aiPrompt, setAiPrompt] = useState('Optimize for low risk')
  const [queryText, setQueryText] = useState('')
  const [response, setResponse] = useState<any>(null)
  const [intcData, setIntcData] = useState<StockLatest | null>(null)
  const [aaplData, setAaplData] = useState<StockLatest | null>(null)
  const [marketData, setMarketData] = useState<{ [key: string]: YFinanceData }>({})
  const [error, setError] = useState('')
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([
    { sender: 'assistant', text: 'Hello! I\'m your financial assistant. How can I help you today?' },
  ])
  const [portfolioData, setPortfolioData] = useState<PortfolioData | null>(null)
  const [stockData, setStockData] = useState<StockData | null>(null)

  const callEndpoint = async (endpoint: string, method: string, data: any = null) => {
    setError('')
    try {
      const url = endpoint === 'portfolio' ? `${API_GATEWAY_URL}/api/portfolio/${userId}` : `${API_GATEWAY_URL}/api/${endpoint}`
      const options = {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: data ? JSON.stringify(data) : null,
      }
      const res = await fetch(url, options)
      if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.statusText}`)
      const resData = await res.json()
      if (endpoint === 'stock-latest/INTC') setIntcData(resData)
      else if (endpoint === 'stock-latest/AAPL') setAaplData(resData)
      else setResponse(resData)
      return resData
    } catch (e: any) {
      setError(e.message)
      return null
    }
  }

  const callGeminiAPI = async (query: string) => {
    if (!GEMINI_API_KEY || GEMINI_API_KEY === 'YOUR_GEMINI_API_KEY') {
      return { content: 'Gemini API key not provided. Mock response: Tech stocks are showing positive momentum this quarter.' }
    }
    try {
      const res = await fetch(`${GEMINI_API_URL}?key=${GEMINI_API_KEY}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ contents: [{ parts: [{ text: query }] }] }),
      })
      if (!res.ok) throw new Error(`Gemini API error: ${res.status}`)
      const data = await res.json()
      return data.candidates[0].content
    } catch (e: any) {
      setError(`Gemini API error: ${e.message}`)
      return null
    }
  }

  const fetchMarketData = async () => {
    const tickers = ['^GSPC', '^IXIC', '^DJI', '^TNX']
    const data: { [key: string]: YFinanceData } = {}
    for (const ticker of tickers) {
      try {
        const res = await fetch(`${API_GATEWAY_URL}/api/yfinance/${ticker}`)
        if (res.ok) data[ticker] = await res.json()
      } catch (e: any) {
        setError(`Failed to fetch yfinance data for ${ticker}: ${e.message}`)
      }
    }
    setMarketData(data)
  }

  useEffect(() => {
    if (activeTab === 'Dashboard') fetchMarketData()
  }, [activeTab])

  return (
    <div className="flex h-screen bg-gray-900 text-white overflow-hidden">
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
      <div className="flex-1 flex flex-col overflow-hidden">
        <TopBar activeTab={activeTab} />
        <div className="flex-1 overflow-y-auto p-6">
          {error && (
            <div className="bg-red-100 text-red-700 p-4 mb-4 rounded-lg">
              <strong>Error:</strong> {error}
            </div>
          )}
          {activeTab === 'Dashboard' && (
            <Dashboard
              marketData={marketData}
              intcData={intcData}
              aaplData={aaplData}
              stockData={stockData}
              ticker={ticker}
              setTicker={setTicker}
              callEndpoint={callEndpoint}
              setStockData={setStockData}
            />
          )}
          {activeTab === 'AI Assistant' && (
            <AIAssistant
              userId={userId}
              queryText={queryText}
              setQueryText={setQueryText}
              chatMessages={chatMessages}
              setChatMessages={setChatMessages}
              callEndpoint={callEndpoint}
              callGeminiAPI={callGeminiAPI}
            />
          )}
          {activeTab === 'Portfolio' && (
            <Portfolio
              userId={userId}
              portfolioData={portfolioData}
              response={response}
              setPortfolioData={setPortfolioData}
              callEndpoint={callEndpoint}
            />
          )}
          {activeTab === 'Simulation' && (
            <Simulation
              userId={userId}
              amount={amount}
              setAmount={setAmount}
              stocks={stocks}
              setStocks={setStocks}
              aiPrompt={aiPrompt}
              setAiPrompt={setAiPrompt}
              response={response}
              callEndpoint={callEndpoint}
            />
          )}
          {activeTab === 'Insights' && (
            <Insights
              userId={userId}
              response={response}
              callEndpoint={callEndpoint}
            />
          )}
          {activeTab === 'Profile' && (
            <Profile
              response={response}
              callEndpoint={callEndpoint}
            />
          )}
          {activeTab === 'Settings' && (
            <Settings userId={userId} setUserId={setUserId} />
          )}
        </div>
      </div>
    </div>
  )
}

export default App