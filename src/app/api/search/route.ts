import { NextRequest, NextResponse } from "next/server";

const {
  AZURE_API_KEY,
  AZURE_API_VERSION,
  AZURE_ENDPOINT,
  AZURE_DEPLOYMENT,
  NEXT_BRAVE_KEY,
} = process.env;

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const company = formData.get("company")?.toString().trim();

    if (!company) {
      return NextResponse.json({ error: "Missing 'company'" }, { status: 400 });
    }

    // Step 1: Generate intelligent queries
    const queryGenRes = await fetch(
      `${AZURE_ENDPOINT}openai/deployments/${AZURE_DEPLOYMENT}/chat/completions?api-version=${AZURE_API_VERSION}`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "api-key": AZURE_API_KEY,
        },
        body: JSON.stringify({
          messages: [
            {
              role: "system",
              content:
                "You're an assistant generating smart, real-world queries to help a B2B sales agent research a company using public search engines with latest news for 2025.",
            },
            {
              role: "user",
              content: `Generate 5 diverse and detailed Brave Search queries to research "${company}". Cover areas like:
- Recent partnerships or launches
- Market strategy or positioning
- Leadership changes or interviews
- Hiring trends or layoffs
- Financial or investor-related news`,
            },
          ],
          temperature: 0.3,
        }),
      }
    );

    const queryGenData = await queryGenRes.json();
    const queryText = queryGenData.choices?.[0]?.message?.content || "";
    const searchQueries = queryText
      .split(/\n/)
      .map((line: string) => line.replace(/^- /, "").trim())
      .filter(Boolean)
      .slice(0, 5);

    // Step 2: Brave search per query
    const braveResults: {
      query: string;
      results: { title: string; url: string; description: string }[];
    }[] = [];

    for (const query of searchQueries) {
      const braveRes = await fetch(
        `https://api.search.brave.com/res/v1/web/search?q=${encodeURIComponent(query)}&count=10`,
        {
          headers: {
            Accept: "application/json",
            "X-Subscription-Token": NEXT_BRAVE_KEY!,
          },
        }
      );

      const braveJson = await braveRes.json();
      const top = (braveJson.web?.results || []).slice(0, 5).map((item: any) => ({
        title: item.title,
        url: item.url,
        description: item.description,
      }));

      braveResults.push({ query, results: top });
    }

    // Step 3: Format for GPT summarization
    const summaryInput = braveResults
      .map((block) => {
        const formatted = block.results
          .map(
            (r) =>
              `• Title: ${r.title}\n  URL: ${r.url}\n  Description: ${r.description}`
          )
          .join("\n\n");

        return `🔍 Query: "${block.query}"\n${formatted}`;
      })
      .join("\n\n======================\n\n");

    // Step 4: GPT summarization
    const finalSummaryRes = await fetch(
      `${AZURE_ENDPOINT}openai/deployments/${AZURE_DEPLOYMENT}/chat/completions?api-version=${AZURE_API_VERSION}`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "api-key": AZURE_API_KEY,
        },
        body: JSON.stringify({
          messages: [
            {
              role: "system",
              content:
                "You're a B2B sales intelligence assistant. Based on the search results, write 3–5 concise bullet points summarizing useful insights about the company for strategic outreach.",
            },
            {
              role: "user",
              content: `Company: ${company}\n\nSearch Results:\n\n${summaryInput}`,
            },
          ],
          temperature: 0.3,
        }),
      }
    );

    const summaryJson = await finalSummaryRes.json();
    const summaryText = summaryJson.choices?.[0]?.message?.content || "";

    return NextResponse.json({
      message: "Company insights retrieved successfully",
      data: {
        company,
        searchQueries,
        summary: summaryText.trim(),
        sources: braveResults.flatMap((b) => b.results.map((r) => r.url)),
      },
    });
  } catch (error) {
    console.error("❌ Error:", error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Unknown error" },
      { status: 500 }
    );
  }
}
