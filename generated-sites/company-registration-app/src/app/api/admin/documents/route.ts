import {put} from "@vercel/blob";import {NextResponse} from "next/server";import {requireAdmin} from "@/lib/auth";import {db} from "@/db";import {cases,documents} from "@/db/schema";import {eq} from "drizzle-orm";

const MAX_FILE_SIZE=10*1024*1024;
const ALLOWED_TYPES=new Set(["application/pdf","image/jpeg","image/png","image/webp"]);

function safeName(name:string){return name.replace(/[^a-zA-Z0-9._-]/g,"_").slice(-120)||"document"}

export async function POST(request:Request){
  try{await requireAdmin()}catch{return NextResponse.json({error:"UNAUTHORIZED"},{status:401})}
  const form=await request.formData();
  const file=form.get("file");
  const caseId=String(form.get("caseId")??"");
  if(!(file instanceof File)||!caseId)return NextResponse.json({error:"فایل و پرونده الزامی است."},{status:400});
  if(file.size<=0||file.size>MAX_FILE_SIZE)return NextResponse.json({error:"حجم فایل باید بین ۱ بایت و ۱۰ مگابایت باشد."},{status:400});
  if(!ALLOWED_TYPES.has(file.type))return NextResponse.json({error:"نوع فایل مجاز نیست."},{status:400});
  const [existingCase]=await db.select({id:cases.id}).from(cases).where(eq(cases.id,caseId)).limit(1);
  if(!existingCase)return NextResponse.json({error:"پرونده پیدا نشد."},{status:404});
  const blob=await put("cases/"+caseId+"/"+Date.now()+"-"+safeName(file.name),file,{access:"public",addRandomSuffix:true});
  const [doc]=await db.insert(documents).values({caseId,name:safeName(file.name),url:blob.url,pathname:blob.pathname,mimeType:file.type,size:file.size}).returning();
  return NextResponse.json(doc);
}