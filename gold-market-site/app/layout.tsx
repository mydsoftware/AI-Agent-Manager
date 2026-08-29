import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'قیمت لحظه‌ای طلا و سکه',
  description: 'نمایش قیمت طلا و سکه با داده‌های TGJU',
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="fa" dir="rtl"><body>{children}</body></html>;
}