import axios from 'axios';
import dotenv from 'dotenv';
import {QuoteSummary, QuotesResponse} from '../types/quoteResponse';
const TRADIER_KEY = process.env.TRADIER_KEY;

export async function fetchQuote(ticker: string): Promise<QuoteSummary> {
  const endpoint = 'https://sandbox.tradier.com/v1/markets/quotes'
  const response: QuotesResponse = await axios.get(endpoint, {
    params: { symbols: ticker },
    headers: { Authorization: `Bearer ${TRADIER_KEY}`, Accept: 'application/json' }
  });
  
  const quote = response.data.quotes.quote;

  return {
    symbol: quote.symbol,
    description: quote.description,
    price: Number(((quote.ask + quote.bid)/2).toFixed(2)),
    change_percentage: quote.change_percentage
  };
}