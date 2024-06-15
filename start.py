import main
import time

loop_times = 0
while True:
    loop_times = loop_times + 1
    print(f">>>loop {loop_times} start")
    main.main()
    time.sleep(10)
    print(f">>>loop {loop_times} end")