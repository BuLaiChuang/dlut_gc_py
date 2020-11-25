# encoding=utf-8

import multiprocessing
import os


def proc_func(msg):
    if __name__ == "__main__":
        print("this is processing - ", msg)
        print(os.getpid())  # 获取进程id
    while 1:  # 死循环，阻止进程退出
        pass


if __name__ == "__main__":
    proc = multiprocessing.Process(  # 准备一个子进程，该进程执行proc_func函数,并且为这个函数传递一个字符串参数"proc 1"
        target=proc_func,
        args=("proc 1",)
    )
    proc.start()  # 启动进程
    proc.join()  # 等待子进程运行结束后再继续执行下一语句
    print("Sub-process done.")