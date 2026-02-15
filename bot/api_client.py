import aiohttp

API_URL = "http://127.0.0.1:8000"


async def get_categories():
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}/categories") as resp:
            return await resp.json()


async def get_subcategories(cat_id: int):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}/subcategories/{cat_id}") as resp:
            return await resp.json()


async def get_products(sub_id: int):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}/products/{sub_id}") as resp:
            return await resp.json()
