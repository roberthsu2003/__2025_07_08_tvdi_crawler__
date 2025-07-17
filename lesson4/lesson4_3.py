#範例 4.2：模擬非同步網路請求

import asyncio
import time
async def task(id, delay):
    print(f"開始任務 {id}")
    await asyncio.sleep(delay)
    print(f"任務 {id} 完成")

# async def main():
#     start = time.time()
#     # 使用 asyncio 來執行非同步任務
#     # 解釋為何還是執行花費3秒
#     # 因為這裡的任務是串行執行的，
#     # 每個任務都需要等待前一個任務完成
#     # 如果要實現真正的非同步，應該使用 asyncio.gather
#     # 或 asyncio.create_task 來並行執行任務
#     # 這樣可以讓多個任務同時進行，節省時間
#     await task(1, 1)
#     await task(2, 2)
#     print(f"總耗時: {time.time() - start:.2f} 秒")

async def main():
    start = time.time()
    # 使用 asyncio 來執行非同步任務
    # 解釋為何還是執行花費3秒
    # 因為這裡的任務是串行執行的，
    # 每個任務都需要等待前一個任務完成
    # 如果要實現真正的非同步，應該使用 asyncio.gather
    # 或 asyncio.create_task 來並行執行任務
    # 這樣可以讓多個任務同時進行，節省時間
    tasks = [task(1,1), task(2, 2)]
    await asyncio.gather(*tasks)
    print(f"總耗時: {time.time() - start:.2f} 秒")

asyncio.run(main())