import AppNav from "@/components/AppNav";
import "./globals.css";

export const metadata = {
  title: "智服通 AgentOps",
  description: "企业智能客服 Agent 运营中台",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN">
      <body>
        <AppNav />
        <main className="site-main">{children}</main>
      </body>
    </html>
  );
}
