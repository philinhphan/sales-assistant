from news_info_agent import search_company_news

# Example standalone invocation. In production your Node layer will pass
# the desired company string – nothing else – to `create_news_info_agent`.
# Here we hard‑code one for a quick smoke test.

if __name__ == "__main__":
    agent = search_company_news("Microsoft")
    print("Agent successfully created:", agent)
