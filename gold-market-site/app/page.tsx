'use client';
import { useCallback,useEffect,useMemo,useState } from 'react';
import Link from 'next/link';

type Prices=Record<string,number|null>; type ApiData={prices:Prices;fetchedAt?:string;error?:string};
const items=[['gold18','طلای ۱۸ عیار','گرم'],['gold24','طلای ۲۴ عیار','گرم'],['coinEmami','سکه امامی','قطعه'],['coinBahar','سکه بهار آزادی','قطعه'],['coinHalf','نیم سکه','قطعه'],['coinQuarter','ربع سکه','قطعه'],['coinGram','سکه گرمی','قطعه'],['usd','دلار آزاد','اسکناس'],['ounce','اونس طلا','اونس']] as const;
const format=(v:number|null)=>v==null?'—':new Intl.NumberFormat('fa-IR').format(v);
export default function Home(){
 const [data,setData]=useState<ApiData|null>(null);const[loading,setLoading]=useState(true);const[q,setQ]=useState('');
 const load=useCallback(async()=>{try{const r=await fetch('/api/prices',{cache:'no-store'});setData(await r.json())}catch{setData({error:'ارتباط با سرویس قیمت برقرار نشد.'})}finally{setLoading(false)}},[]);
 useEffect(()=>{load();const t=setInterval(load,10000);return()=>clearInterval(t)},[load]);
 const filtered=useMemo(()=>items.filter(x=>x[1].includes(q)),[q]);const time=data?.fetchedAt?new Date(data.fetchedAt).toLocaleTimeString('fa-IR'):'در حال دریافت';
 return <main className="page-shell"><header className="hero"><div><span className="eyebrow">بازار طلا، سکه و ارز</span><h1>مرکز هوشمند قیمت بازار</h1><p>داده‌های لحظه‌ای TGJU با بروزرسانی خودکار و آماده تحلیل AI.</p></div><div className="status"><span className={data?.error?'dot bad':'dot'}/>{data?.error?'خطا':'آنلاین'}</div></header>
 <div className="toolbar"><input value={q} onChange={e=>setQ(e.target.value)} placeholder="جستجوی طلا، سکه، دلار..."/><span>بروزرسانی: ۱۰ ثانیه</span></div>{data?.error&&<div className="error">{data.error}</div>}
 <section className="grid">{filtered.map(([key,title,unit])=><Link href={`/market/${key}`} className="card" key={key}><div className="card-title">{title}</div><div className="price">{loading?'...':format(data?.prices?.[key]??null)}</div><div className="meta">ریال / {unit}<span className="arrow">←</span></div></Link>)}</section>
 <section className="feature"><div><b>تحلیل هوشمند بازار</b><p>در صفحات اختصاصی هر نماد، داده تاریخی را به Agent Manager می‌فرستیم تا تحلیل روند، سناریو و خلاصه بازار تولید شود.</p></div><span>AI AGENT</span></section>
 <footer><span>آخرین دریافت: {time}</span><span>منبع: TGJU</span></footer></main>;
}