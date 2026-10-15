import React, { useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { Search, CheckCircle2, ChevronLeft, BookOpen, ClipboardCheck, Home, FileText, Users, Scale, ShieldCheck, Menu, X, Star, ArrowLeft, LockKeyhole } from 'lucide-react';
import './styles.css';

const modules = [
  { id:'m1', title:'شروع کار و ذهنیت مشاور', icon:Users, lessons:[
    ['نقش مشاور حرفه‌ای','تفاوت واسطه، فروشنده و مشاور؛ اخلاق حرفه‌ای؛ محرمانگی؛ تعارض منافع و مسئولیت حرفه‌ای.'],
    ['شناخت بازار محلی','محله، زیرمحله، دسترسی‌ها، قیمت‌های مقایسه‌ای، عرضه و تقاضا و ساختن حافظه قیمتی.'],
    ['واژگان ضروری املاک','شش‌دانگ، عرصه، اعیان، قدرالسهم، مشاع، مفروز، رهن، بازداشت، کاربری، پایان‌کار و تفکیکی.'],
    ['چرخه کامل معامله','مسیر استاندارد از ورود مالک و خریدار تا بازدید، مذاکره، بررسی مدارک و امضای قرارداد.']
  ]},
  { id:'m2', title:'گرفتن فایل از مالک', icon:Home, lessons:[
    ['تماس اول با مالک','سؤالات طلایی درباره انگیزه فروش، زمان، قیمت، وضعیت سکونت، مدارک و محدودیت‌های معامله.'],
    ['فرم کارشناسی فایل','ثبت متراژ، سن، طبقه، تعداد واحد، پارکینگ، انباری، آسانسور، جهت، نور، بازسازی و ایرادات.'],
    ['بازدید و قیمت‌گذاری اولیه','تفکیک قیمت پیشنهادی مالک از قیمت قابل معامله و شناخت عوامل افزایش یا کاهش ارزش.'],
    ['عکاسی و معرفی فایل','ترتیب عکس‌ها، عنوان آگهی، متن دقیق، ثبت مزایا و پرهیز از ادعاهای اثبات‌نشده.'],
    ['فایل واقعی یا فایل مرده','تشخیص مالک آماده معامله از مالک صرفاً قیمت‌گیر و تعیین زمان پیگیری.']
  ]},
  { id:'m3', title:'کارشناسی فنی و ظاهری ملک', icon:ClipboardCheck, lessons:[
    ['موقعیت و ساختمان','کوچه، عرض گذر، دسترسی، جهت، نما، تعداد طبقات و واحدها و اثر آنها بر مطلوبیت.'],
    ['پارکینگ و انباری','اختصاصی یا مشاع، مزاحم، ابعاد، مسیر دسترسی و تطبیق محل با مدارک.'],
    ['آسانسور و مشاعات','ظرفیت، لرزش، توقف، نگهداری، نظافت، راه‌پله، نور و آثار رطوبت.'],
    ['داخل واحد','نورگیری، نقشه، پرت، کف، دیوار، سقف، پنجره، درب و کمدها.'],
    ['آشپزخانه و کابینت','ملامینه، هایگلاس، اکریلیک، ممبران، روکش چوب، تمام‌چوب، صفحات و یراق.'],
    ['تأسیسات','برق، گاز، آب، پکیج، کولر، موتورخانه، فاضلاب و نشانه‌های نم و نشتی.'],
    ['بازسازی واقعی','تشخیص بازسازی زیرساختی از زیباسازی سطحی و شناخت اثر آن بر ارزش بازار.'],
    ['ترک، نم و ایرادات','تفکیک ایراد ظاهری از مورد نیازمند بررسی مهندس یا کارشناس متخصص.']
  ]},
  { id:'m4', title:'پیدا کردن و نیازسنجی خریدار', icon:Users, lessons:[
    ['ورود مشتری','شروع مکالمه، ایجاد اعتماد و تشخیص نیاز واقعی بدون فشار برای خرید.'],
    ['نیازسنجی حرفه‌ای','بودجه، محدوده، متراژ، طبقه، پارکینگ، آسانسور، زمان خرید و خط قرمزها.'],
    ['کشف بودجه واقعی','تفاوت توان مالی، بودجه اعلامی و سقف قابل تصمیم‌گیری.'],
    ['تطبیق فایل با مشتری','انتخاب چند گزینه مناسب به جای ارسال انبوه و بی‌هدف.'],
    ['مدیریت بازدید','هماهنگی مالک، زمان‌بندی، ترتیب نمایش و حفظ تمرکز مشتری.']
  ]},
  { id:'m5', title:'بازدید و ارائه ملک', icon:BookOpen, lessons:[
    ['سناریوی بازدید','چه چیزی را اول نشان دهیم، چه زمانی سکوت کنیم و چگونه سؤال درست بپرسیم.'],
    ['بیان مزایا و ایرادات','پنهان نکردن عیب، توضیح شفاف و تبدیل ایراد قابل مذاکره به داده تصمیم‌گیری.'],
    ['شناخت سیگنال خرید','سؤالات مشتری، مدت ماندن در ملک و نشانه‌های رضایت، تردید یا رد.'],
    ['مقایسه فایل‌ها','ساخت مقایسه ذهنی بر اساس موقعیت، مشخصات، کیفیت و قیمت.'],
    ['بازدید دوم','چه چیزهایی باید دوباره بررسی شود و چگونه مشتری را برای تصمیم نهایی آماده کنیم.']
  ]},
  { id:'m6', title:'قیمت‌گذاری و مذاکره', icon:Scale, lessons:[
    ['قیمت‌گذاری مقایسه‌ای','انتخاب فایل‌های مشابه و تعدیل بابت متراژ، طبقه، سن، امکانات، جهت و کیفیت.'],
    ['قیمت اعلامی، کارشناسی و معامله','سه عدد متفاوت و کاربرد هرکدام در مذاکره.'],
    ['عوامل مؤثر بر قیمت','موقعیت، زمین، سن بنا، نقشه، نور، پارکینگ، کیفیت ساخت و وضعیت بازار.'],
    ['مذاکره با مالک','کشف کف واقعی، امتیازدهی مرحله‌ای و جلوگیری از شکستن بی‌دلیل قیمت.'],
    ['مذاکره با خریدار','مدیریت پیشنهاد، زمان، بیعانه و شروط بدون وعده غیرواقعی.'],
    ['مدیریت بن‌بست','وقتی اختلاف قیمت زیاد است چه داده‌هایی را دوباره بررسی کنیم.']
  ]},
  { id:'m7', title:'بررسی حقوقی و مدارک', icon:ShieldCheck, lessons:[
    ['هویت و مالکیت','احراز هویت طرفین و تطبیق مالک، وکیل یا نماینده با مدارک.'],
    ['سند و مشخصات ملک','مساحت، حدود، پلاک، مشخصات واحد و مغایرت‌های احتمالی.'],
    ['رهن، بازداشت و بدهی','مواردی که باید پیش از تعهد مالی جدی روشن شوند.'],
    ['پایان‌کار و تفکیکی','اهمیت مدارک ساختمانی و تطبیق واحد، پارکینگ و انباری.'],
    ['وکالت و نمایندگی','ریسک‌های وکالت‌نامه و مواردی که نیاز به بررسی حقوقی و استعلام دارند.'],
    ['وراث و چندمالکی','لزوم شناسایی همه ذی‌نفعان و کنترل اختیار امضاکننده.'],
    ['مرز مسئولیت مشاور','چه چیزهایی را نباید بدون متخصص حقوقی یا فنی قطعی اعلام کرد.']
  ]},
  { id:'m8', title:'از توافق تا امضای قرارداد', icon:FileText, lessons:[
    ['جمع‌بندی توافق','مشخصات دقیق ملک، ثمن، زمان‌بندی، نحوه پرداخت و تعهدات.'],
    ['پیش‌نویس قرارداد','کنترل نام‌ها، اعداد، تاریخ‌ها، شروط، پیوست‌ها و مشخصات ملک.'],
    ['شروط مهم','تحویل، تخلیه، فک رهن، دفترخانه، خسارت و وجه التزام؛ با رعایت مقررات جاری.'],
    ['کنترل نهایی قبل از امضا','یک دور خواندن کامل و تطبیق توافق شفاهی با متن مکتوب.'],
    ['امضای نهایی','احراز هویت، امضاها، اثر انگشت در صورت رویه معتبر، نسخه‌ها و مستندسازی.'],
    ['پس از امضا','پیگیری تعهدات بعدی تا انتقال یا تحویل، بدون ورود خارج از صلاحیت حرفه‌ای.']
  ]},
  { id:'m9', title:'مهارت‌های حرفه‌ای', icon:Star, lessons:[
    ['ساخت حافظه قیمتی','ثبت فایل‌های معامله‌شده و مقایسه آنها برای شناخت بازار محلی.'],
    ['مدیریت پیگیری','زمان‌بندی تماس، ثبت نتیجه و جلوگیری از پیگیری آزاردهنده.'],
    ['اعتمادسازی','شفافیت، مستندسازی، خوش‌قولی و پرهیز از اغراق.'],
    ['اشتباهات مرگبار','دروغ درباره قیمت، پنهان‌کاری، قول حقوقی بدون تخصص و بی‌نظمی.']
  ]}
];

const allLessons = modules.flatMap(m => m.lessons.map((l,i) => ({ module:m.title, title:l[0], text:l[1], key:`${m.id}-${i}` })));

function App(){
  const [active,setActive]=useState('all');
  const [q,setQ]=useState('');
  const [done,setDone]=useState(()=>{try{return JSON.parse(localStorage.getItem('reAcademyDone')||'[]')}catch{return []}});
  const [open,setOpen]=useState(null);
  const [menu,setMenu]=useState(false);
  const filtered=useMemo(()=>allLessons.filter(x=>(!q||x.title.includes(q)||x.module.includes(q)||x.text.includes(q))&&(active==='all'||modules.find(m=>m.title===x.module)?.id===active)),[q,active]);
  const toggle=k=>setDone(d=>{const n=d.includes(k)?d.filter(x=>x!==k):[...d,k];localStorage.setItem('reAcademyDone',JSON.stringify(n));return n});
  const pct=Math.round(done.length/allLessons.length*100);
  return <div className="app">
    <header><div className="brand"><div className="logo">ام</div><div><b>آکادمی مشاور املاک</b><span>دوره آموزشی صفر تا صد</span></div></div><button className="mobile" onClick={()=>setMenu(!menu)}>{menu?<X/>:<Menu/>}</button><div className="progress"><span>پیشرفت یادگیری</span><strong>{pct}%</strong><div><i style={{width:pct+'%'}}/></div></div></header>
    <div className="layout"><aside className={menu?'show':''}><div className="sideTitle">نقشه مسیر آموزش</div><button className={active==='all'?'active':''} onClick={()=>{setActive('all');setMenu(false)}}>همه درس‌ها <b>{allLessons.length}</b></button>{modules.map(m=><button key={m.id} className={active===m.id?'active':''} onClick={()=>{setActive(m.id);setMenu(false)}}><m.icon size={17}/>{m.title}<b>{m.lessons.length}</b></button>)}</aside>
      <main><section className="hero"><div><div className="eyebrow">REAL ESTATE ACADEMY</div><h1>مشاور املاک حرفه‌ای شو؛<br/><em>از صفر تا امضای قرارداد</em></h1><p>یک دوره آموزشی مرحله‌به‌مرحله برای شناخت بازار، فایل‌گیری، کارشناسی ملک، نیازسنجی مشتری، بازدید، قیمت‌گذاری، مذاکره و کنترل فرآیند قرارداد.</p><div className="stats"><div><strong>{modules.length}</strong><span>ماژول</span></div><div><strong>{allLessons.length}</strong><span>درس آموزشی</span></div><div><strong>{done.length}</strong><span>تکمیل‌شده</span></div></div></div><div className="heroCard"><ShieldCheck size={28}/><b>اصل آموزشی</b><p>در موضوعات فنی و حقوقی، تشخیص اولیه با اعلام نظر قطعی متخصص یکی نیست. همیشه مرز صلاحیت حرفه‌ای را رعایت کن.</p></div></section>
        <div className="toolbar"><div className="search"><Search size={19}/><input value={q} onChange={e=>setQ(e.target.value)} placeholder="جستجو در درس‌ها..."/></div><span>{filtered.length} درس</span></div>
        <div className="cards">{filtered.map((x,i)=><article className={'lesson '+(done.includes(x.key)?'finished':'')} key={x.key} onClick={()=>setOpen(x)}><div className="lessonTop"><span className="num">{i+1}</span><span className="module">{x.module}</span>{done.includes(x.key)&&<CheckCircle2 size={18}/>}</div><h3>{x.title}</h3><p>{x.text}</p><div className="learn">مطالعه درس <ChevronLeft size={17}/></div></article>)}</div>
        <section className="field"><div><span className="eyebrow">یادگیری میدانی</span><h2>ترتیب نگاه یک مشاور در بازدید</h2><p>موقعیت → ساختمان → پارکینگ → مشاعات → نورگیری → نقشه → تأسیسات → کیفیت داخلی → مدارک → قیمت.</p></div><button onClick={()=>setOpen({title:'چک‌لیست آموزشی بازدید ملک',module:'تمرین میدانی',text:'برای تمرین، هر بار یک ملک را در همین ترتیب ذهنی بررسی کن. ابتدا موقعیت و ساختمان را ببین، سپس پارکینگ و مشاعات، بعد داخل واحد و در پایان مدارک و عوامل قیمت. هدف تمرین، ساختن چشم کارشناسی است؛ نه صدور نظر رسمی کارشناسی.'})}>مطالعه چک‌لیست <ArrowLeft size={18}/></button></section>
      </main></div>
    {open&&<div className="overlay" onClick={()=>setOpen(null)}><div className="modal" onClick={e=>e.stopPropagation()}><button className="close" onClick={()=>setOpen(null)}><X/></button><span className="eyebrow">{open.module}</span><h2>{open.title}</h2><p>{open.text}</p><div className="note"><LockKeyhole size={18}/><span>محتوای این صفحه آموزشی است. در امور حقوقی، فنی و قراردادهای واقعی، قوانین و نظر متخصص مربوطه باید ملاک عمل باشد.</span></div>{open.key&&<button className="complete" onClick={()=>toggle(open.key)}>{done.includes(open.key)?'✓ درس تکمیل شده':'علامت‌گذاری به‌عنوان تکمیل‌شده'}</button>}</div></div>}
  </div>;
}
createRoot(document.getElementById('root')).render(<App/>);
