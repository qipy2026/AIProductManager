import Link from "next/link";
import "./globals.css";

export const metadata = {
  title: "智服通 AgentOps",
  description: "B2B 智能客服 Agent 运营中台",
};

const nav = [
  { href: "/chat", label: "对话" },
  { href: "/ops", label: "运营后台" },
  { href: "/eval", label: "评测报告" },
];

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN">
      <body>
        <header style={{ borderBottom: "1px solid #eee", padding: "12px 24px" }}>
          <div style={{ maxWidth: 960, margin: "0 auto", display: "flex", gap: 24, alignItems: "center" }}>
            <strong>智服通 AgentOps</strong>
            <nav style={{ display: "flex", gap: 16 }}>
              {nav.map((item) => (
                <Link key={item.href} href={item.href} style={{ color: "#0066cc" }}>
                  {item.label}
                </Link>
              ))}
            </nav>
          </div>
        </header>
        <main style={{ maxWidth: 960, margin: "0 auto", padding: 24 }}>{children}</main>
      </body>
    </html>
  );
}
