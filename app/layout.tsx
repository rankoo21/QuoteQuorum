import type {Metadata} from 'next';import './globals.css';
export const metadata:Metadata={title:'QuoteQuorum — Bounded Market Snapshots',description:'Three-source quote consensus on GenLayer Studionet.'};
export default function RootLayout({children}:{children:React.ReactNode}){return <html lang="en"><body>{children}</body></html>}
