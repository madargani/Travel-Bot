import './globals.css'

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html
      lang="en" 
      className="box-border"
    >
      <body>{children}</body>
    </html>
  );
}
