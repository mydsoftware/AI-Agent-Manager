import type {Metadata} from "next";import "./globals.css";
export const metadata:Metadata={title:"خدمات ثبت آراد | ثبت شرکت",description:"خدمات تخصصی ثبت شرکت و پیگیری پرونده"};
export default function RootLayout({children}:{children:React.ReactNode}){return <html lang="fa" dir="rtl"><body>{children}</body></html>}