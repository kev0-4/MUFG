import type { RecommendationData, SentimentData } from '../types'

interface InsightsProps {
  userId: string
  response: RecommendationData | SentimentData | null
  callEndpoint: (endpoint: string, method: string, data?: any) => Promise<any>
}

const Insights = ({ userId, response, callEndpoint }: InsightsProps) => {
  return (
    <div className="bg-gray-800 rounded-xl border border-gray-700 p-6">
      <h2 className="text-xl font-bold mb-4">Insights</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <button
            onClick={() => callEndpoint('recommend', 'POST', { user_id: userId })}
            className="bg-primary-500 hover:bg-primary-600 text-white px-4 py-2 rounded-lg text-sm transition-colors flex items-center mb-4"
          >
            <span className="material-symbols-outlined mr-1">insights</span>
            Get Recommendations
          </button>
          {/* {response?.recommended_strategy && (
            <div className="bg-gray-700/50 p-4 rounded-lg">
              <p className="text-lg font-bold">Strategy: {response.recommended_strategy}</p>
              <p>Return: {response.portfolio_return}%</p>
              <p>Stocks: {response.stocks.join(', ')}</p>
            </div>
          )} */}
        </div>
        <div>
          <button
            onClick={() => callEndpoint('stock-sentiments', 'POST', { user_id: userId })}
            className="bg-primary-500 hover:bg-primary-600 text-white px-4 py-2 rounded-lg text-sm transition-colors flex items-center mb-4"
          >
            <span className="material-symbols-outlined mr-1">mood</span>
            Analyze Sentiments
          </button>
          {response && Object.keys(response).length > 0 && !response.recommended_strategy && (
            <div className="bg-gray-700/50 p-4 rounded-lg">
              {Object.entries(response).map(([stock, data]: [string, any]) => (
                <p key={stock}>
                  {stock}: {data.sentiment} ({data.confidence})
                </p>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Insights