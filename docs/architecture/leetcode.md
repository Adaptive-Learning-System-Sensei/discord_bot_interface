# LeetCode Feature Engineering

Tracks developer metrics and processes problem-solving queries straight through user Discord chats.

## Sub-component Interactions

1. **Trigger**: User requests information in a command routed to `src/bot/cogs/leetcode_cog.py`.
2. **Business Rule Engine**: Data passes through rules defined inside `src/core/domains/leetcode/`.
3. **External Fetching**: Downstream network execution triggers queries via the `src/web/external_apis/leetcode_wrapper_apis.py` handler.
