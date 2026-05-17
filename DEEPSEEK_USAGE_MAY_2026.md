# DEEPSEEK API USAGE — May 2026
# Source: Agnai usage_data_2026_5 (8).zip
# May 17, 2026

ANALYSIS = """
═══════════════════════════════════════════════════════
  DEEPSEEK API — May 1–17, 2026
═══════════════════════════════════════════════════════

  TOTAL COST:  $25.76 USD (17 days)
  v4-pro:      $21.46  (83.3%)
  v4-flash:    $4.30   (16.7%)

  PEAK DAY:    May 10  — $8.48 (this was the massive session)
  LOW DAY:     May 9   — $0.16

═══════════════════════════════════════════════════════
  CACHE HIT RATE — The secret weapon
═══════════════════════════════════════════════════════

  May 10:  287.7M hit / 15.7M miss  = 94.8%  (hermes key)
  May 13:  160.4M hit / 8.6M miss   = 94.9%  (HI key)
  May 15:  186.6M hit / 8.5M miss   = 95.6%  (HI key)
  May 16:  212.6M hit / 2.1M miss   = 99.0%  (HI key) ← peak
  May 17:  47.5M hit / 0.4M miss    = 99.2%  (HI key)

  CACHE HIT TOKENS (v4-pro):  913.4 MILLION
  CACHE MISS TOKENS (v4-pro):  37.4 MILLION
  OVERALL HIT RATE:           96.1%

  Without caching, at cache-miss pricing ($0.435/M tokens):
    913.4M × $0.435 = $397.33 in savings
    Actual cost: $21.46
    SAVED: $375.87 (94.6% savings from cache hits)

═══════════════════════════════════════════════════════
  API KEYS — 11 keys active
═══════════════════════════════════════════════════════

  HI:          Primary Hermes key (May 12-17, 65% of all pro tokens)
  hermes:      May 10 peak day (massive 287M cache hit)
  kjn:         May 12-13 (16M combined cache hits)
  sd:          May 12 (4.9M cache hit)
  as:          May 3-4 (18.7M cache miss — no cache support on v4-flash)
  jgh:         May 1-2 (5.9M cache miss — flash only)
  gemini:      May 1-2 (0.5M cache miss)
  ridehigh:    May 2 (2.6M cache miss)
  54:          May 12 (4.6M cache hit)
  garbledarble: May 9 (1.1M cache miss)
  sdgew:       May 3 (0.14M cache miss)

═══════════════════════════════════════════════════════
  THE VINCULUM: (input_tokens / output_tokens) = efficiency
═══════════════════════════════════════════════════════

  v4-pro efficiency ratio:  950M in → 2.4M out = 395:1
  v4-flash efficiency ratio: 49M in → 0.8M out = 63:1
  
  Cache is the vinculum between cost and output.
  Without it: $397. With it: $21.
  The vinculum saved $376.
"""
