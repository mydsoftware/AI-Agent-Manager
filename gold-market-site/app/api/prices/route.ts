import { NextResponse } from 'next/server';
import * as cheerio from 'cheerio';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

const SOURCE_URL = 'https://www.tgju.org/local-markets';
const wanted = [
  ['طلای 18 عیار / 750', 'gold18'], ['طلای ۲۴ عیار', 'gold24'],
  ['سکه امامی تک فروشی', 'coinEmami'], ['سکه بهار آزادی تک فروشی', 'coinBahar'],
  ['نیم سکه تک فروشی', 'coinHalf'], ['ربع سکه تک فروشی', 'coinQuarter'],
  ['سکه گرمی تک فروشی', 'coinGram'], ['دلار', 'usd'], ['انس طلا', 'ounce'],
] as const;

function normalize(text: string) { return text.replace(/\u200c/g, ' ').replace(/\s+/g, ' ').trim(); }
function digits(text: string) { return text.replace(/[۰-۹]/g, d => String('۰۱۲۳۴۵۶۷۸۹'.indexOf(d))).replace(/[٠-٩]/g, d => String('٠١٢٣٤٥٦٧٨٩'.indexOf(d))).replace(/,/g, ''); }
function numberFrom(text: string) { const n = digits(text).replace(/[^0-9.-]/g, ''); return n ? Number(n) : null; }

function findRow($: cheerio.CheerioAPI, label: string) {
  let row: string[] | null = null;
  $('tr').each((_, el) => {
    if (row) return;
    const cells = $(el).find('td,th').map((__, cell) => normalize($(cell).text())).get();
    if (cells.some(c => c === label || c.includes(label))) row = cells;
  });
  return row;
}

function findPrice($: cheerio.CheerioAPI, label: string) {
  const row = findRow($, label);
  if (!row) return null;
  const candidate = row.map(numberFrom).find(n => n !== null && n >= 100);
  return candidate ?? null;
}

function findChange($: cheerio.CheerioAPI, label: string) {
  const row = findRow($, label);
  if (!row) return { amount: null, percent: null };
  const values = row.map(numberFrom).filter((n): n is number => n !== null);
  return { amount: values.length > 1 ? values[1] : null, percent: null };
}

export async function GET() {
  try {
    const response = await fetch(SOURCE_URL, { headers: { 'User-Agent': 'Mozilla/5.0 (compatible; GoldMarketSite/1.0)' }, cache: 'no-store' });
    if (!response.ok) throw new Error(`TGJU HTTP ${response.status}`);
    const $ = cheerio.load(await response.text());
    const prices = Object.fromEntries(wanted.map(([label, key]) => [key, findPrice($, label)]));
    const changes = Object.fromEntries(wanted.map(([label, key]) => [key, findChange($, label)]));
    return NextResponse.json({ source: 'TGJU', sourceUrl: SOURCE_URL, unit: 'ریال', fetchedAt: new Date().toISOString(), prices, changes }, { headers: { 'Cache-Control': 'no-store, max-age=0' } });
  } catch (error) {
    return NextResponse.json({ source: 'TGJU', error: error instanceof Error ? error.message : 'خطای نامشخص در دریافت داده' }, { status: 502 });
  }
}