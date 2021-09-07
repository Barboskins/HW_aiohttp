import asyncio
from aiohttp import ClientSession

async def get_post(post_id):
    async with ClientSession() as session:
        async with session.get(f"http://127.0.0.1:8080/post/{post_id}") as resp:
            return await resp.text()


async def create_posts():
    async with ClientSession() as session:
        async with session.post(f"http://127.0.0.1:8080/post", json={
            " header": "header",
            "text": "some text",
        }) as resp:
            if resp.status != 201:
                return await resp.text()
            return await resp.json()

async def delete_post(post_id):
    async with ClientSession() as session:
        async with session.delete(f"http://127.0.0.1:8080/post/{post_id}") as resp:
            return {"status": resp.status}


async def main():
    response = await get_post()
    print(response)
    response = await create_posts()
    print(response)
    response = await delete_post()
    print(response)