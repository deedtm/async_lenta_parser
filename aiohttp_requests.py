from asyncio import sleep
import sys
from aiohttp import ClientSession
from logging import info, warning
import json


with open("request_data.json", "r") as f:
    req_data: dict[dict] = json.load(f)
    skus: dict = req_data["skus"]
    stores: dict = req_data["stores"]
    cookies: dict = req_data["cookies"]
    headers: dict = req_data["headers"]

SECONDS = 150


async def get_store(session: ClientSession, city_name: str, address: str):
    async with session.get(url=stores["url"], headers=headers) as res:
        if res.status == 433:
            warning(msg=f"Слишком частые запросы. Повтор попытки через {SECONDS} сек.")
            await sleep(SECONDS)

            return await get_store(session, address, city_name)
        elif res.status == 401:
            info(msg="Требуется обновить куки")
            sys.exit(0)

        info(msg=f"{res.status} {res.reason}")
        for store in await res.json(encoding="utf8"):
            if address in store["address"] and city_name in store["cityName"]:
                return store


async def get_products(
    session: ClientSession, store_id: str, city_key: str, node_code: str, offset: int = -1
):
    cookies["StoreSubDomainCookie"] = store_id
    cookies["Store"] = store_id
    cookies["CityCookie"] = str(city_key)
    cookies["CitySubDomainCookie"] = str(city_key)
    offset = 0 if offset == -1 else offset
    payload = skus["data"].replace("{offset}", str(offset)).replace("{node_code}", node_code)

    async with session.post(
        url=skus["url"],
        headers=headers,
        cookies=cookies,
        data=payload,
    ) as res:
        if res.status == 433:
            warning(msg=f"Слишком частые запросы. Повтор попытки через {SECONDS} сек.")
            await sleep(SECONDS)

            return await get_products(session, store_id, city_key, offset)
        elif res.status == 401:
            info(msg="Требуется обновить куки")
            sys.exit(0)

        info(msg=f"{res.status} {res.reason}")
        products = await res.json()
        total_count = products["totalCount"]
        urls = {product["code"]: product["skuUrl"] for product in products["skus"]}
        if offset == 0:
            return total_count, urls
        else:
            return urls
