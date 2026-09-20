import { cookies } from "next/headers";
import crypto from "node:crypto";
const COOKIE="arad_admin_session";
function sign(value:string){return crypto.createHmac("sha256",process.env.SESSION_SECRET!).update(value).digest("hex")}
export function sessionValue(){const payload=Buffer.from(JSON.stringify({email:process.env.ADMIN_EMAIL,exp:Date.now()+604800000})).toString("base64url");return payload+"."+sign(payload)}
export function verifySession(value?:string){if(!value||!process.env.SESSION_SECRET)return false;const [payload,signature]=value.split(".");if(!payload||!signature)return false;const expected=sign(payload);if(signature.length!==expected.length||!crypto.timingSafeEqual(Buffer.from(signature),Buffer.from(expected)))return false;try{const data=JSON.parse(Buffer.from(payload,"base64url").toString());return data.email===process.env.ADMIN_EMAIL&&data.exp>Date.now()}catch{return false}}
export async function isAdmin(){const store=await cookies();return verifySession(store.get(COOKIE)?.value)}
export async function requireAdmin(){if(!(await isAdmin()))throw new Error("UNAUTHORIZED")}
export {COOKIE};