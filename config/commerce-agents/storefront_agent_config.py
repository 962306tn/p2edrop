# Copyright 2026 Shopify Inc.
# SPDX-License-Identifier: Apache-2.0

"""The all vibes space deployment's shopping agent config: an anonymous storefront over a
live shop, so no disclosures, and ids ground through Shopify's gid form.

Replaces storefront/api/agent_config.py in the checkout. The two clauses about order
tracking are asserted by storefront/api/tests/test_checkout_orders.py; keep them when
editing the notes.
"""

from __future__ import annotations

from shopping_agent import ShoppingAgentConfig


def build_shopping_config(store_name: str) -> ShoppingAgentConfig:
    return ShoppingAgentConfig(
        brand_name=store_name,
        assistant_name="the store assistant",
        brand_voice="warm, direct, and plain about what a refill actually covers",
        domain_search_notes=(
            "The catalog is a live Shopify store priced in USD, built around one product "
            "line: a cordless dry-mist pet odor gun and the refill pods it takes. A "
            "product's purchasable options are its variants in get_product_details, and "
            "the cart holds variants, never the family. Two option axes run through the "
            "catalog: scent (lemon, lavender, peppermint, fresh linen) and how much is in "
            "the box (the gun alone, or the gun with refill pods). Treat a scent as a "
            "preference to ask about rather than a filter to guess at, and read the pod "
            "count off the variant rather than estimating how long a bundle lasts. "
            "Checkout, shipping, and payment all happen on the store's own checkout page "
            "— hand the customer to it rather than promising delivery options. Order "
            "lookups need a credential grant this deployment may not have: when the order "
            "tools return nothing, say so plainly and point the customer at their Shopify "
            "order confirmation email for status and tracking."
        ),
        product_id_patterns=(r"gid://shopify/(?:Product|ProductVariant)/\d+",),
    )
