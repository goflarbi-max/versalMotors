## Metrics verification - Oct 1 2026
Checked for double-counting, list_price vs net_sale_price mix, nulls dropped.
Result: Fixed import path and schema. Verified revenue via raw SQL vs metrics.py - exact match. 3/3 tests passed.

## Decisions confirmed - Oct 2 2026
1. Complaint co-occurrence: Combined rule - same sale_id OR same customer_id within 30 days.
2. Default scan: Report latest complete month, use up to 12 prior months as context for trends.
3. Severity threshold: Suppress <40 from management output, retain when include_low_severity=True.
4. Inventory categories: Use vehicle_segment + condition only, exclude branch initially for stronger sample sizes.

## AI Mistakes Log - Day 3 onwards
Format: Date | Prompt | Wrong Answer | Correct Answer | Fix



- Error on 'Which branch has highest complaints?': 404 models/gemini-1.5-flash is not found for API version v1beta, or is not supported for generateContent. Call ModelService.ListModels to see the list of available models and their supported methods.
## Stress-test timing attribution

- **Situation:** I initially treated a 24.4-second subprocess measurement as Data Quality page load time.
- **How discovered:** A phased `AppTest` measurement separated Streamlit shell startup from child-page rendering and showed 11.9 seconds of test-shell startup, 3.625 seconds for the cold page, and 1.182 seconds for a cached rerun.
- **How corrected:** I recorded the isolated timings in `docs/test_log.md`, retained the useful caching/query-batching improvements, and stopped attributing process startup overhead to the page itself.
