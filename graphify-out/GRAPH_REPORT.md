# Graph Report - CodeAlpha_ E-commerce Store  (2026-06-02)

## Corpus Check
- 26 files · ~35,167 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 125 nodes · 184 edges · 23 communities (10 shown, 13 thin omitted)
- Extraction: 70% EXTRACTED · 30% INFERRED · 0% AMBIGUOUS · INFERRED: 55 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 22|Community 22]]

## God Nodes (most connected - your core abstractions)
1. `OrderItem` - 20 edges
2. `Order` - 19 edges
3. `StoreTestCase` - 17 edges
4. `Product` - 14 edges
5. `Category` - 13 edges
6. `Wishlist` - 13 edges
7. `OrderAdmin` - 10 edges
8. `LowStockFilter` - 8 edges
9. `ProductAdmin` - 8 edges
10. `RegisterForm` - 7 edges

## Surprising Connections (you probably didn't know these)
- `OrderItemInline` --uses--> `OrderItem`  [INFERRED]
  ecommerce/store/admin.py → ecommerce/store/models.py
- `LowStockFilter` --uses--> `OrderItem`  [INFERRED]
  ecommerce/store/admin.py → ecommerce/store/models.py
- `CategoryAdmin` --uses--> `OrderItem`  [INFERRED]
  ecommerce/store/admin.py → ecommerce/store/models.py
- `Media` --uses--> `OrderItem`  [INFERRED]
  ecommerce/store/admin.py → ecommerce/store/models.py
- `ProductAdmin` --uses--> `OrderItem`  [INFERRED]
  ecommerce/store/admin.py → ecommerce/store/models.py

## Import Cycles
- None detected.

## Communities (23 total, 13 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.18
Nodes (12): CategoryAdmin, LowStockFilter, Media, OrderItemAdmin, OrderItemInline, ProductAdmin, WishlistAdmin, Category (+4 more)

### Community 1 - "Community 1"
Cohesion: 0.11
Nodes (11): CheckoutForm, LoginForm, Meta, ProductSearchForm, RegisterForm, OrderItem, checkout(), home() (+3 more)

### Community 3 - "Community 3"
Cohesion: 0.40
Nodes (4): Features, Notes, Setup, ShopEase E-commerce Django Project

### Community 4 - "Community 4"
Cohesion: 0.27
Nodes (5): closeMobileNav(), getCSRFToken(), getFocusableElements(), openMobileNav(), updateQuantityOnServer()

### Community 19 - "Community 19"
Cohesion: 0.50
Nodes (3): builds, routes, version

### Community 22 - "Community 22"
Cohesion: 0.50
Nodes (3): builds, routes, version

## Knowledge Gaps
- **14 isolated node(s):** `Migration`, `Migration`, `Meta`, `version`, `builds` (+9 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **13 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `StoreTestCase` connect `Community 20` to `Community 0`, `Community 1`?**
  _High betweenness centrality (0.095) - this node is a cross-community bridge._
- **Why does `OrderItem` connect `Community 1` to `Community 0`, `Community 2`, `Community 20`?**
  _High betweenness centrality (0.061) - this node is a cross-community bridge._
- **Why does `Order` connect `Community 0` to `Community 1`, `Community 2`, `Community 20`?**
  _High betweenness centrality (0.052) - this node is a cross-community bridge._
- **Are the 14 inferred relationships involving `OrderItem` (e.g. with `CategoryAdmin` and `LowStockFilter`) actually correct?**
  _`OrderItem` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 14 inferred relationships involving `Order` (e.g. with `CategoryAdmin` and `LowStockFilter`) actually correct?**
  _`Order` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `StoreTestCase` (e.g. with `Category` and `Order`) actually correct?**
  _`StoreTestCase` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `Product` (e.g. with `CategoryAdmin` and `LowStockFilter`) actually correct?**
  _`Product` has 9 INFERRED edges - model-reasoned connections that need verification._