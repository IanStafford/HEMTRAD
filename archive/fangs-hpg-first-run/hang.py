import time
open("partial.txt", "w").write("x")
print("hanging", flush=True)
time.sleep(3600)
