'use client';

import { useCallback, useEffect, useState } from 'react';

type Prices = Record<string, number | null>;

type ApiData = { prices: Prices; fetchedAt?: string; error?: string; source?: string };

const items = [
  ['gold18', 'طلای ۱۸ عیار', 'گرم'],
  ['gold24', 'طلای ۲۴ عیار', 'گرم'],
  ['coinEmami', 'سکه امامی', 'قطعه'],
  ['coinBahar', 'سکه بهار آزادی', 'قطعه'],
  ['coinHalf', 'نیم سکه', 'قطعه'],
  ['coinQuarter', 'ربع سکه', 'قطعه'],
  ['coinGram', 'سکه گرمی', 'قطعه'],
] as const;

const format = (value: number | null) => value == null ? '—' : new Intl.NumberFormat('fa-IR').format(value);

export default function Home() {
  const [data, setData] = useState<ApiData | null>(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    try {
      const response = await fetch('/api/prices', { cache: 'no-store' });
      const json = await response.json();
      setData(json);
    } catch {
      setData({ error: 'ارتباط با سرویس قیمت برقرار نشد.' });
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
    const timer = setInterval(load, 10000);
    return () => clearInterval(timer);
  }, [load]);

  const time = data?.fetchedAt ? new Date(data.fetchedAt).toLocaleTimeString('fa-IR') : 'در حال دریافت';

  return (
    <main className="page-shell">
      <header className="hero">
        <div>
          <span className="eyebrow">بازار طلا و سکه</span>
          <h1>قیمت لحظه‌ای طلا و سکه</h1>
          <p>داده‌ها از TGJU دریافت و هر ۱۰ ثانیه تازه‌سازی می‌شوند.</p>
        </div>
        <div className="status"><span className={data?.error ? 'dot bad' : 'dot'} /> {data?.error ? 'خطا' : 'آنلاین'}</div>
      </header>

      {data?.error && <div className="error">{data.error}</div>}

      <section className="grid">
        {items.map(([key, title, unit]) => (
          <article className="card" key={key}>
            <div className="card-title">{title}</div>
            <div className="price">{loading ? '...' : format(data?.prices?.[key] ?? null)}</div>
            <div className="meta">ریال / {unit}</div>
          </article>
        ))}
      </section>

      <footer>
        <span>آخرین دریافت: {time}</span>
        <span>منبع: TGJU</span>
      </footer>
    </main>
  );
}