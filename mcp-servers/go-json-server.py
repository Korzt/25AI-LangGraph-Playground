from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("ProductCatalog")

# Constants
API_BASE = "http://localhost:3000/api/products"
USER_AGENT = "product-catalog-app/1.0"

async def make_request(url: str) -> list[dict[str, Any]] | None:
    """Make a GET request and return JSON list or None on failure."""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None

@mcp.tool()
async def list_products(category: str | None = None) -> str:
    """List all products, optionally filtered by category.

    Args:
        category: Optional product category to filter by (e.g., electronics)
    """
    data = await make_request(API_BASE)
    if not data:
        return "Unable to fetch product data."

    # If category filter provided, filter products
    if category:
        filtered = [p for p in data if p.get("category") == category.lower()]
    else:
        filtered = data

    if not filtered:
        return f"No products found in category '{category}'."

    # Format product info nicely
    result_lines = []
    for p in filtered:
        line = (
            f"ID: {p['id']}\n"
            f"Name: {p['name']}\n"
            f"Category: {p['category']}\n"
            f"Price: ${p['price']:.2f}\n"
            f"In Stock: {'Yes' if p['in_stock'] else 'No'}\n"
            f"Rating: {p['rating']}/5\n"
            f"Tags: {', '.join(p['tags'])}\n"
            f"Created At: {p['created_at']}\n"
            "-----"
        )
        result_lines.append(line)

    return "\n".join(result_lines)

if __name__ == "__main__":
    mcp.run(transport='stdio')
