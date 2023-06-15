from multiprocessing import Pool
import time


def times(args):
    time.sleep(10)
    default = 1
    print(f"Process : {args}")
    for a in args:
        default *= a
    print(default)
    return default


running_proc = []

a = [[2, 100, 5120], [90, 652, 547, 1958, 23], [90, 1235, 653]]

count = 0
if __name__ == "__main__":
    pool = Pool(processes=2)
    pool.map(times, a)
    pool.close()
    pool.join()
# process = [None] * 2
# joining_index = 0
# for i in a:
#     if joining_index == 0:
#         joining_index = 1
#     elif joining_index == 1:
#         joining_index = 0
#     print(joining_index)
#     print(process)
#     p = Process(target=times, args=i)
#     if None not in process:
#         print("Join")
#         process[joining_index].join()
#         print("Done")
#     else:
#         process[joining_index].run()
