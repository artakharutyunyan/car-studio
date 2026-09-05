import type { Metadata } from 'next';
import './globals.css';
export const metadata: Metadata = { title: 'Car Studio — The Collection', description: 'Explore iconic road cars and Formula 1 machines in an interactive 3D studio.', icons:{icon:'/car-studio-favicon.png',apple:'/apple-touch-icon.png'} };
export const viewport = {width:'device-width',initialScale:1,viewportFit:'cover'};
export default function RootLayout({children}:{children:React.ReactNode}) { return <html lang="en" className="dark"><body>{children}</body></html> }
