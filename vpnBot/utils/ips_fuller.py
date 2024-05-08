import asyncio

from tqdm import tqdm

from vpnBot.db.manager import db_manager
from vpnBot.db.tables import Ips


async def main():
    for i in tqdm(range(100, 120)):
        ips = Ips(
            ipv4=f'10.66.66.{i}/32',
            ipv6=f'fd42:42:42::{i}/128'
        )
        await db_manager.add_record(ips)


if __name__ == '__main__':
    asyncio.run(main())
