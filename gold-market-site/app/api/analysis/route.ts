import { NextRequest, NextResponse } from 'next/server';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function POST(req: NextRequest) {
  const base = process.env.AGENT_MANAGER_URL;
  if (!base) return NextResponse.json({configured:false, message:'AGENT_MANAGER_URL تنظیم نشده است.'}, {status:503});
  try {
    const body = await req.json();
    const token = process.env.AGENT_MANAGER_TOKEN;
    const response = await fetch(`${base.replace(/\/$/,'')}/api/market-analysis`, {
      method:'POST', headers:{'Content-Type':'application/json', ...(token?{Authorization:`Bearer ${token}`}:{})},
      body: JSON.stringify({source:'tgju', ...body})
    });
    const text = await response.text();
    return new NextResponse(text, {status:response.status, headers:{'Content-Type':response.headers.get('content-type')||'application/json'}});
  } catch(error) { return NextResponse.json({configured:true, error:error instanceof Error?error.message:'خطای اتصال به Agent Manager'}, {status:502}); }
}