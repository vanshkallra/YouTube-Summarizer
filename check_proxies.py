import threading
import queue

import requests

q = queue.Queue()
lock = threading.Lock() 
TEST_URL = "https://httpbin.org/ip" 
valid_proxies=[]

with open("proxy_list.txt","r") as f:
    proxies = f.read().split("\n")
    for p in proxies:
        q.put(p)

def check_proxies():
    global q
    while not q.empty():
        proxy=q.get()
        try:
            res = requests.get(TEST_URL,
                               proxies={"http": proxy,
                                        "https:": proxy})
        except:
            continue
        if res.status_code == 200:
            print(proxy)

for _ in range(10):
    threading.Thread(target=check_proxies).start()


# import threading
# import queue
# import requests
# from requests.exceptions import RequestException

# q = queue.Queue()
# valid_proxies = []
# lock = threading.Lock()  # For thread-safe list operations
# TEST_URL = "https://httpbin.org/ip"  # Better test endpoint
# TIMEOUT = 5  # Seconds to wait for response

# def load_proxies(filename):
#     with open(filename, "r") as f:
#         return [p.strip() for p in f if p.strip()]

# def check_proxies():
#     global q
#     while True:
#         try:
#             proxy = q.get_nowait()
#         except queue.Empty:
#             break
            
#         try:
#             response = requests.get(
#                 TEST_URL,
#                 proxies={
#                     "http": f"http://{proxy}",
#                     "https": f"http://{proxy}"  # Many proxies use HTTP for HTTPS
#                 },
#                 timeout=TIMEOUT
#             )
            
#             if response.status_code == 200:
#                 with lock:
#                     valid_proxies.append(proxy)
#                     print(proxy)
                    
#         except RequestException as e:
#             continue
#         finally:
#             q.task_done()

# def main():
#     global q
    
#     # Load proxies from file
#     proxies = load_proxies("proxy_list.txt")
#     if not proxies:
#         print("No proxies found in file")
#         return
        
#     for p in proxies:
#         q.put(p)
    
#     # Create and start threads
#     threads = []
#     for _ in range(10):
#         t = threading.Thread(target=check_proxies)
#         t.start()
#         threads.append(t)
    
#     # Wait for all tasks to complete
#     q.join()
    
#     # Print final results
#     print("\nValidation complete:")
#     print(f"Total valid proxies: {len(valid_proxies)}")
#     # print("Valid proxies list:", valid_proxies)

# if __name__ == "__main__":
#     main()
