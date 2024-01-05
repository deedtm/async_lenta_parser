import asyncio
import aiohttp
import logging
import json
from aiohttp_requests import get_products, get_store
from excel import Excel
from selenium_processes import close_driver, get_driver, get_stock
from utils import save_to_json


with open("other.json", "r") as f:
    other: dict[dict] = json.load(f)


async def generate_products_json(
    products: dict,
    total_count: int,
    session: aiohttp.ClientSession,
    store_id: str,
    city_key: str,
    node_code: str
):
    output = None
    try:
        for offset in range(24, total_count + 1, 24):
            products = products | await get_products(
                session, store_id, city_key, node_code, offset
            )
            await asyncio.sleep(1.5)
    except Exception as e:
        output = f"{e.__class__.__name__}: {e.__str__()}"
    finally:
        save_to_json("products", products)
        return output


def get_stocks_list(store_id, city_key):
    with open("products.json", "r") as f:
        products: dict[str] = json.load(f)
    urls = [products[product] for product in products]
    driver = get_driver(store_id, city_key)
    stocks = [get_stock(url, driver) for url in urls]
    close_driver(driver)

    return stocks


async def main():
    async with aiohttp.ClientSession() as session:
        store = await get_store(
            session,
            input("[INPUT] Введите город или слово, входящее в него (напр. Петербург): ").capitalize(),
            input("[INPUT] Введите адрес или слово, входящее в него (напр. Вербная): ").capitalize()
        )
        if not store:
            logging.error(msg="Неверно введен адрес или город")
        else:
            for category in other["node_codes"]:
                logging.info(msg=f'Начат парсинг категории "{category}"')
                node_code = other["node_codes"][category]

                total_count, products = await get_products(
                    session, store["id"], store["cityKey"], node_code
                )
                res = await generate_products_json(
                    products,
                    total_count,
                    session,
                    store["id"],
                    store["cityKey"],
                    node_code,
                )

                if res is not None:
                    logging.error(msg=f"Произошла ошибка {res}")
                else:
                    stocks = get_stocks_list(store["id"], store["cityKey"])

                    xls = Excel("data", category, ["Артикул", "Наличие"])
                    sheet = xls.get_sheet(category)
                    ind = 0
                    for art in products:
                        if ind >= len(stocks):
                            break
                        xls.write(sheet, [art, stocks[ind]])
                        ind += 1


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(filename)s:%(funcName)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    asyncio.run(main())
    input('[FINAL] Парсинг завершился. Нажмите Enter, чтобы выйти.')
