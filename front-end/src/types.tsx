export interface Stock {
  ticker: string
  description: string
  price: string
  change_percentage: string
}

export interface ChartData {
  symbol: string
  strike: string
  date_str: string
  value: string
  tooltipContent: string
}

export interface HeatmapData {
  stockData: Stock
  metric_str: string
  direction: string
  data: ChartData[]
  dims: Dims
  changeType: string
}

export interface Dims {
  width: number
  height: number
}

export interface Option {
  symbol: string
  direction: string
  date: string
  date_str: string
  strike: string
  volume: string
  open_interest: string
  price: string
  spread: string
  delta: string
  gamma: string
  theta: string
  vega: string
  rho: string
  phi: string
}

export interface GetDataResponse {
  ticker: string;
  description: string;
  updated_at: string;
  price: string;
  change_percentage: string;
  expirationDates: string[];
  expirationDatesStringified: string[];
  strikes: number[];
  options: Option[];
}