import { NextRequest, NextResponse } from "next/server";
import { tavily } from "@tavily/core";

const {
  AZURE_API_KEY,
  AZURE_API_VERSION,
  AZURE_ENDPOINT,
  AZURE_DEPLOYMENT,
  NEXT_BRAVE_KEY,
  TAVILY_API_KEY,
} = process.env;

type SearchHit = {
  title: string;
  url: string;
  description: string;
  source: "brave" | "tavily";
};

const tavilyClient = tavily({ apiKey: TAVILY_API_KEY! });

/* ---------- search helpers ---------- */

async function braveSearch(query: string, topN = 5): Promise<SearchHit[]> {
  const res = await fetch(
    `https://api.search.brave.com/res/v1/web/search?q=${encodeURIComponent(query)}&count=${topN}`,
    {
      headers: {
        Accept: "application/json",
        "X-Subscription-Token": NEXT_BRAVE_KEY!,
      },
    }
  );
  const json = await res.json();
  return (json.web?.results || [])
    .slice(0, topN)
    .map((it: any) => ({
      title: it.title,
      url: it.url,
      description: it.description,
      source: "brave",
    }));
}

async function tavilySearch(query: string, topN = 5): Promise<SearchHit[]> {
  const { results } = await tavilyClient.search(query, {
    max_results: topN,
    topic: "news",
    include_answer: false,
    include_raw_content: false,
  });
  return results.map((it: any) => ({
    title: it.title,
    url: it.url,
    description: it.snippet ?? "",
    source: "tavily",
  }));
}

/* ---------- utils ---------- */

function mergeDedup(...lists: SearchHit[][]): SearchHit[] {
  const seen = new Set<string>();
  const out: SearchHit[] = [];
  for (const hit of lists.flat()) {
    if (!seen.has(hit.url)) {
      seen.add(hit.url);
      out.push(hit);
    }
  }
  return out;
}

function toString(hit: SearchHit): string {
  return `${hit.title} | ${hit.url} | ${hit.description.slice(0, 160)}`;
}

/* ---------- route handler ---------- */

export async function POST(req: NextRequest) {
  try {
    const formData = await req.formData();
    const company = formData.get("company")?.toString().trim();
    if (!company) {
      return NextResponse.json({ error: "Missing 'company'" }, { status: 400 });
    }

    /* 1 ─ create five search queries with GPT */
    const qJson = await (
      await fetch(
        `${AZURE_ENDPOINT}openai/deployments/${AZURE_DEPLOYMENT}/chat/completions?api-version=${AZURE_API_VERSION}`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json", "api-key": AZURE_API_KEY },
          body: JSON.stringify({
            messages: [
              {
                role: "system",
                content:
                  "You're an assistant generating diverse, late‑2025 search queries for B2B company research.",
              },
              {
                role: "user",
                content: `Create 5 Brave/Tavily search queries to research "${company}", covering recent news, partnerships, leadership changes, hiring trends, and financial updates and only be limited to "${company}".`,
              },
            ],
            temperature: 0.0,
          }),
        }
      )
    ).json();

    const queries = (qJson.choices?.[0]?.message?.content ?? "")
      .split(/\n/)
      .filter((l: string) => /^[-\d.*•]/.test(l))
      .map((l: string) => l.replace(/^[-\d.*•]\s*/, "").trim())
      .slice(0, 5);

    /* 2 ─ fetch Brave + Tavily results */
    const braveStrings: string[] = [];
    const tavilyStrings: string[] = [];
    const allHits: SearchHit[] = [];

    for (const q of queries) {
      const [braveHits, tavilyHits] = await Promise.all([
        braveSearch(q, 5),
        tavilySearch(q, 5),
      ]);

      braveHits.forEach((h) => braveStrings.push(toString(h)));
      tavilyHits.forEach((h) => tavilyStrings.push(toString(h)));

      allHits.push(...mergeDedup(braveHits, tavilyHits));
    }

    const allResults = Array.from(new Set([...braveStrings, ...tavilyStrings]));
    const corpus = allHits.map(toString).join("\n\n");

    /* 3 ─ summarise the merged corpus */
    const sumJson = await (
      await fetch(
        `${AZURE_ENDPOINT}openai/deployments/${AZURE_DEPLOYMENT}/chat/completions?api-version=${AZURE_API_VERSION}`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json", "api-key": AZURE_API_KEY },
          body: JSON.stringify({
            messages: [
              {
                role: "system",
                content:
                  "You're a B2B sales intelligence assistant. Summarise the corpus into 3‑5 concise, actionable bullets.",
              },
              { role: "user", content: `Company: ${company}\n\n${corpus}` },
            ],
            temperature: 0.0,
          }),
        }
      )
    ).json();

    const insights = sumJson.choices?.[0]?.message?.content?.trim() ?? "";

    /* 4 ─ respond with expanded payload */
    return NextResponse.json({
      company,
      queries,
      insights,
      totalSources: allHits.length,
      sources: allHits.map((h) => h.url),           // URLs only
      braveResults: braveStrings,                   // array<string>
      tavilyResults: tavilyStrings,                 // array<string>
      allResults,                                   // merged, deduped
    });
  } catch (err) {
    console.error("company‑info POST error:", err);
    return NextResponse.json(
      { error: err instanceof Error ? err.message : "Unknown error" },
      { status: 500 }
    );
  }
}
