import type { ReactNode } from 'react';
import './styles.css';
export const metadata = { title: 'WarehouseOps AI', description: 'An intelligent warehouse operations control tower' };
export default function RootLayout({ children }: { children: ReactNode }) {
  return <html lang="en"><body>{children}</body></html>;
}
