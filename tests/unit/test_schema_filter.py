"""Schema filtering tiers: keyword match and the LLM-guess fallback."""

import os
import sys
import unittest
from unittest import mock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from core.domain.schema_utils import smart_filter_schema


# Six tables, so smart_filter_schema takes the filtering path: a schema of five
# or fewer tables is returned whole without trying to narrow it.
SCHEMA = {
    "orders": [{"name": "id", "type": "INT"}],
    "customers": [{"name": "name", "type": "VARCHAR"}],
    "products": [{"name": "price", "type": "DECIMAL"}],
    "staff": [{"name": "name", "type": "VARCHAR"}],
    "locations": [{"name": "city", "type": "VARCHAR"}],
    "payments": [{"name": "amount", "type": "DECIMAL"}],
}


class TestSmartFilterSchema(unittest.TestCase):
    def test_keyword_match_keeps_only_the_mentioned_table(self):
        """A table named in the question is selected without any LLM call."""
        filtered = smart_filter_schema(SCHEMA, "Show me orders", llm=None)
        self.assertEqual(set(filtered), {"orders"})

    def test_llm_guess_is_used_when_no_keyword_matches(self):
        """With no keyword hit, the guessed tables become the filtered schema."""
        with mock.patch(
            "core.domain.schema_utils._llm_guess_tables",
            return_value={"customers", "products"},
        ) as guess:
            filtered = smart_filter_schema(
                SCHEMA, "Who bought expensive items?", llm=object()
            )
        self.assertTrue(guess.called)
        self.assertEqual(set(filtered), {"customers", "products"})
