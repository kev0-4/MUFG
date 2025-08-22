export interface YFinanceData {
  value: number;
  change: string;
}

export interface StockLatest {
  ticker: string;
  latest_price: { date: string; open: string; high: string; low: string; close: string; volume: string };
  meta: any;
  cache_hit: boolean;
  last_updated: string;
}

export interface StockData {
  ticker: string;
  prices: { date: string; open: string; high: string; low: string; close: string; volume: string }[];
  meta: any;
  cache_hit: boolean;
  last_updated: string;
}

export interface PortfolioData {
  portfolio: { totalValue: number };
  holdings: { symbol: string; assetType: string; quantity: number; purchasePrice: number; currentPrice: number }[];
}

export interface UserData {
  super_balance: number;
}

export interface SimulationData {
  projected_balance: number;
  eli5_response: string;
}

export interface QueryData {
  intent: string;
  query_sentiment: { label: string; score: number };
}

export interface RecommendationData {
  recommended_strategy: string;
  portfolio_return: number;
  stocks: string[];
}

export interface SentimentData {
  [key: string]: { sentiment: string; confidence: number };
}

export interface KeyData {
  public_key?: string;
  private_key?: string;
}

export interface ChatMessage {
  sender: 'user' | 'assistant';
  text: string;
}