import threading
import re
import os
import time
# edit by xinyu.kou@samsung.com


def get_pci_bus_num(disk_num):
   get_pci_cmd = 'find /sys/* -name {0} | grep devices'.format(disk_num)
   hit = os.popen(get_pci_cmd).readlines()
   if hit:
       pci_line_str = hit[0]
       split_hit = re.split('/', pci_line_str)
       return split_hit[-4]

def get_pci_speed(disk_num):
   pci_bus_num = get_pci_bus_num(disk_num)
   get_pci_speed_cmd = "lspci -vvv -s {0} | grep 'LnkSta:' | cut -d ' ' -f 2,4".format(pci_bus_num)
   lspci_info = os.popen(get_pci_speed_cmd).readlines()
   lspci_info_strip = [x.strip('\n') for x in lspci_info][0]
   pci_speed = ''.join(lspci_info_strip.split(','))
   return pci_speed

def get_port_num(nvme_ssd, bus_num):
    
    if len(nvme_ssd)>5:
        cpu_id = '3'
    else:
        cpu_id = '2'

    raw_bus_num_list = re.split(r'[:,.]', bus_num)
    bus_num_str = ' '.join([int(x,16) for x in raw_bus_num_list])
    bus_show = os.popen("./AMDX -i={0} -listport | grep Port | cut -d ' ' -f 6,8,10".format(cpu_id)).readlines()
    for item in bus_show:
        if item == bus_num_str:
            return (cpu_id, bus_show.index(item))
    return 

def get_single_si_result(cpu_id, port_num, times=3):
    
    success_time = 0
    while success_time < times:
        raw_results = os.popen('./AMDX -i={0} -marginport={1},1 -lanes=0-3'.format(cpu_id, port_num)).readlines()
        results = ''.join(raw_results) 
        if 'Querying' not in results:
                success_time += 1
                print('({0},{1}) loop {2} is done.'.format(cpu_id,port_num,success_time))
                time.sleep(2)
        else:
            #print('AMDXIO Tool Failed! ({0},{1}), wait for 10 secs to retry'.format(cpu_id,port_num))
            test_set = (cpu_id,port_num)
            fail_set_list = [cpu_id, port_num]
            fail_set = ','.join(fail_set_list)
            if fail_set not in failed_port:
                failed_port.append(fail_set)
            time.sleep(10)
    running_port.remove((cpu_id,port_num))
    
    print('{0} still running. '.format(str(len(running_port))))
    
    return

def get_cpu_mapping():
    cpu_mapping = {}
    for cpu_id in ('2','3'):
        cpu_port_num_list = os.popen("./AMDX -i={0} -listport | grep -E 'Port Num.*x4.*4'| cut -d ' ' -f 4".format(cpu_id)).readlines()
        if cpu_port_num_list:
            cpu_port_num_list = [str(x.strip('\n')) for x in cpu_port_num_list]    
            cpu_mapping[cpu_id] = cpu_port_num_list
    return cpu_mapping

def port_scan():
    bus_port_map = {}
    bus_speed_map = {}
    for cpu_id in ['2','3']:
        amdxio_result = os.popen("./AMDX -i={0} -listport|grep Port|cut -d ' ' -f 4,6,8,10,15,20".format(cpu_id)).readlines()
        for item in amdxio_result:
            info = item.strip('\n').split(' ')
            port_num = info[0]
            bus_num = [str(int(x,16)) for x in info[1:-2]]
            bus_num_str = ' '.join(bus_num)
            speed = item[-5:-1]
            bus_port_map[bus_num_str] = (cpu_id,port_num)
            bus_speed_map[bus_num_str] = speed

    return bus_speed_map, bus_port_map

def nvme_scan(nvme_list):
    nvme_bus_map = {}
    print('{0} nvme ssd slected, scanning bus number...'.format(len(nvme_list)))
    for nvme_ssd in nvme_list:
        raw_bus_num = get_pci_bus_num(nvme_ssd)
        raw_bus_num_list = re.split(r'[:,.]', raw_bus_num)[1:]
        bus_num = ' '.join(str(int(x,16)) for x in raw_bus_num_list)
        nvme_bus_map[nvme_ssd] = bus_num

    return nvme_bus_map

def start(target_ssd_item):
    thread_list = []
    for k,v in target_ssd_item.items():
        cpu_id, port_num = v[-1]
        t = threading.Thread(target=get_single_si_result, args=(cpu_id, port_num))
        thread_list.append(t)
    for t in thread_list:
        t.start()
    for t in thread_list:
        t.join
    print('All Done!')
    return

def user_select():
    nvme_list = []
    os.system("nvme list | grep '/dev/nvme'")
    select = input('select nvme ssd to start SI test, sep by comma. a for all\n> ')
    if select == 'a':
        raw_nvme_list = os.popen("ls /dev/|grep -E 'nvme[0-9]{1,2}$'").readlines()
        nvme_list = [x.strip('\n') for x in raw_nvme_list]
    elif len(select) == 1:
        nvme_device = 'nvme' + select
        nvme_list.append(nvme_device)
    else:
        nvme_index_str = select.strip('\n')
        nvme_index_list = select.replace(' ','').split(',')
        nvme_list = ['nvme' + x for x in nvme_index_list]
    return nvme_list
     
# ------ Danger ------ #
os.system('echo>complete.txt')
os.system('echo>retry_ports.txt')
failed_port = []
running_port = []
complete_port = []
bus_speed_map, bus_port_map = port_scan()
nvme_list = user_select()
times = input('How many times of SI test per slot?\n> ')
times = int(times.strip('\n'))
nvme_bus_map = nvme_scan(nvme_list)
thread_list = []
for ssd in nvme_list:
    bus_num = nvme_bus_map[ssd]
    speed = bus_speed_map[bus_num]
    cpu_id, port_num = bus_port_map[bus_num]
    running_port.append((cpu_id,port_num))
    bus_str = '-'.join([str(hex(int(x))) for x in bus_num.split(' ')])
    print('{0} bus: {1} speed: {2}'.format(ssd, bus_str, speed))
    t = threading.Thread(target=get_single_si_result, args=(cpu_id, port_num, times))
    thread_list.append(t)
print('Running SI Test Parallel...')
for t in thread_list:
    time.sleep(1)
    t.start()
for t in thread_list:
    t.join()
print('All Done!')

