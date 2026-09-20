import {NextResponse} from "next/server";
import {db} from "@/db";
import {payments} from "@/db/schema";
import {requireAdmin";
export async function POST(request:Request){try{await requireAdmin()}catch{return NextResponse.json({error:"UNAUTHORIZED"},{status:401})}const b=await request.json();if(!b.caseId||!Number.isInteger(b.amount)||b.amount<=0)return NextResponse.json({error:"اطلاعات پرداخت نامعتبر است."},{status:400});const [payment]=await db.insert(payments).values({caseId:b.caseId,amount:b.amount,description:b.description||"هزینه خدمات ثبت شرکت"}).returning();return NextResponse.json({payment,checkoutUrl:"/checkout/"+payment.id})}