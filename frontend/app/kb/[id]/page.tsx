"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

interface KbDoc {
  id: string;
  title: string;
  content: string;
  keywords: string[];
}

export default function KbDocPage({ params }: { params: { id: string } }) {
  const [doc, setDoc] = useState<KbDoc | null>(null);
  const [loading, setLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const res = await fetch(`/api/kb/${encodeURIComponent(params.id)}`);
        if (cancelled) return;
        if (!res.ok) {
          setNotFound(true);
          return;
        }
        setDoc(await res.json());
      } catch {
        if (!cancelled) setNotFound(true);
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [params.id]);

  return (
    <div>
      <p style={{ marginBottom: 16 }}>
        <Link href="/chat" style={{ color: "#0066cc" }}>
          ← 返回对话
        </Link>
      </p>

      {loading && <p style={{ color: "#999" }}>加载文档…</p>}

      {notFound && !loading && (
        <>
          <h1>文档未找到</h1>
          <p style={{ color: "#666" }}>ID: {params.id}</p>
          <p style={{ color: "#999", fontSize: 13 }}>
            请确认后端已启动并包含 /api/kb 接口。
          </p>
        </>
      )}

      {doc && !loading && (
        <>
          <h1>{doc.title}</h1>
          <p style={{ color: "#888", fontSize: 13, marginBottom: 20 }}>{doc.id}</p>
          <div className="panel" style={{ lineHeight: 1.8 }}>
            {doc.content}
          </div>
          {doc.keywords?.length > 0 && (
            <p style={{ marginTop: 16, fontSize: 13, color: "#666" }}>
              关键词：{doc.keywords.join(" · ")}
            </p>
          )}
        </>
      )}
    </div>
  );
}
