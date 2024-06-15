import main
import time

loop_times = 0
while True:
    loop_times = loop_times + 1
    print(">>>loop {looptime} start")
    main.main()
    time.sleep(5)
    print(">>>loop {looptime} end")