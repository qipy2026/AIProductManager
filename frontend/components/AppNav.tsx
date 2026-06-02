"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const nav = [
  { href: "/chat", label: "对话" },
  { href: "/tickets", label: "工单" },
  { href: "/roi", label: "业务 ROI" },
  { href: "/ops", label: "运营后台" },
  { href: "/eval", label: "评测报告" },
];

function isActive(pathname: string, href: string): boolean {
  if (href === "/chat") {
    return pathname === "/" || pathname === "/chat" || pathname.startsWith("/chat/");
  }
  return pathname === href || pathname.startsWith(`${href}/`);
}

export default function AppNav() {
  const pathname = usePathname();

  return (
    <header className="site-header">
      <div className="site-header-inner">
        <Link href="/chat" className="site-brand">
          智服通 AgentOps
        </Link>
        <nav className="site-nav" aria-label="主导航">
          {nav.map((item) => {
            const active = isActive(pathname, item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`site-nav-link ${active ? "site-nav-link-active" : ""}`}
                aria-current={active ? "page" : undefined}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>
      </div>
    </header>
  );
}
