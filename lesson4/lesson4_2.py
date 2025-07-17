import time

def task(id, delay):
    print(f"開始任務 {id}")
    time.sleep(delay)
    print(f"任務 {id} 完成")

start = time.time()
task(1, 1)
task(2, 2)
print(f"總耗時: {time.time() - start:.2f} 秒")