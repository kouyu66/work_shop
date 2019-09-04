import threading
import re
import os

def multiThread(funcname, listname):
    """以列表中元素作为参数，列表元素数作为线程个数，多线程执行指定函数
    阻塞，当所有线程执行完成后才继续主线程"""
    threadIndex = range(len(listname))
    threads = []
    for num in threadIndex:
        t = threading.Thread(target=funcname, args=(listname[num],))
        threads.append(t)
    for num in threadIndex:
        threads[num].start()
    for num in threadIndex:
        threads[num].join()
    return


def get_pci_bus_num(disk_num):
    get_pci_cmd = 'find /sys/* -name {0} | grep devices'.format(disk_num)
    hit = os.popen(get_pci_cmd).readlines()
    if hit:
        pci_line_str = hit[0]
        split_hit = re.split('/', pci_line_str)
        return split_hit[-3]

def get_pci_speed():
    pci_bus_num = get_pci_bus_num()
    get_pci_speed_cmd = "lspci -vvv -s {0} | grep 'LnkSta:' | cut -d ' ' -f 2,4".format(pci_bus_num)
    lspci_info = os.popen(get_pci_speed_cmd).readlines()
    lspci_info_strip = [x.strip('\n') for x in lspci_info][0]
    pci_speed = ''.join(lspci_info_strip.split(','))
    return pci_speed

def count_off(count=23):
    nvme_num = list(range(23))

