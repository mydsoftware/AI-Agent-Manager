import { NextResponse } from 'next/server';
import * as cheerio from 'cheerio';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

const SOURCE_URL = 'https://www.tgju.org/local-markets';

const wanted = [
  ['طلای 18 عیار / 750', 'gold18'],
  ['طلای ۲۴ عیار', 'gold24'],
  ['سکه امامی تک فروشی', 'coinEmami'],
  ['سکه بهار آزادی تک فروشی', 'coinBahar'],
  ['نیم سکه تک فروشی', 'coinHalf'],
  ['ربع سکه تک فروشی', 'coinQuarter'],
  ['سکه گرمی تک فروشی', 'coinGram'],
] as const;

function normalize(text: string) {
  return text.replace(/\u200c/g, ' ').replace(/\s+/g, ' ').trim();
}

function digitsToEnglish(text: string) {
  return text
    .replace(/[۰-۹]/g, (d) => String('۰۱۲۳۴۵۶۷۸۹'.indexOf(d)))
    .replace(/[٠-٩]/g, (d) => String('٠١٢٣٤٥٦٧٨٩'.indexOf(d)))
    .replace(/,/g, '');
}

function findPrice($: cheerio.CheerioAPI, label: string) {
  let value: string | null = null;
  $('tr').each((_, row) => {
    if (value) return;
    const cells = $(row).find('td,th').map((__, cell) => normalize($(cell).text())).get();
    if (cells.some((cell) => cell === label || cell.includes(label))) {
      const candidate = cells.find((cell) => /\d/.test(digitsToEnglish(cell)) && digitsToEnglish(cell).replace(/\D/g, '').length >= 5);
      if (candidate) value = digitsToEnglish(candidate).replace(/\D/g, '');
    }
  });
  return value ? Number(value) : null;
}

export async function GET() {
  try {
    const response = await fetch(SOURCE_URL, {
      headers: { 'User-Agent': 'Mozilla/5.0 (compatible; GoldMarketSite/1.0)' },
      cache: 'no-store',
    });
    if (!response.ok) throw new Error(`TGJU HTTP ${response.status}`);
    const html = await response.text();
    const $ = cheerio.load(html);

    const prices = Object.fromEntries(wanted.map(([label, key]) => [key, findPrice($, label)]));
    const missing = Object.entries(prices).filter(([, value]) => value === null).map(([key]) => key);
    if (missing.length > 0) throw new Error(`داده‌های TGJU کامل دریافت نشد: ${missing.join(', ')}`);

    return NextResponse.json({
      source: 'TGJU',
      sourceUrl: SOURCE_URL,
      unit: 'ریال',
      fetchedAt: new Date().toISOString(),
      prices,
    }, { headers: { 'Cache-Control': 'no-store, max-age=0' } });
  } catch (error) {
    return NextResponse.json({
      source: 'TGJU',
      error: error instanceof Error ? error.message : 'خطای نامشخص در دریافت داده',
    }, { status: 502 });
  }
}