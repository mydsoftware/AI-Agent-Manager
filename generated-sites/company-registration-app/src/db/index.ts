import postgres from "postgres";
import { drizzle } from "drizzle-orm/postgres-js";
import * as schema from "./schema";
const globalForDb=globalThis as unknown as {sql?:ReturnType<typeof postgres>};
export const sql=globalForDb.sql??postgres(process.env.DATABASE_URL!,{prepare:false,max:5});
if(process.env.NODE_ENV!=="production")globalForDb.sql=sql;
export const db=drizzle(sql,{schema});