import threading
import re
import os
import time
# edit by xinyu.kou@samsung.com

failed_port = []

#def get_pci_bus_num(disk_num):
#    get_pci_cmd = 'find /sys/* -name {0} | grep devices'.format(disk_num)
#    hit = os.popen(get_pci_cmd).readlines()
#    if hit:
#        pci_line_str = hit[0]
#        split_hit = re.split('/', pci_line_str)
#        return split_hit[-3]

#def get_pci_speed():
#    pci_bus_num = get_pci_bus_num()
#    get_pci_speed_cmd = "lspci -vvv -s {0} | grep 'LnkSta:' | cut -d ' ' -f 2,4".format(pci_bus_num)
#    lspci_info = os.popen(get_pci_speed_cmd).readlines()
#    lspci_info_strip = [x.strip('\n') for x in lspci_info][0]
#    pci_speed = ''.join(lspci_info_strip.split(','))
#    return pci_speed

def get_single_si_result(cpu_id, port_num, times=3):
    success_time = 0
    while success_time < times:
        raw_results = os.popen('./AMDX -i={0} -marginport={1},1 -lanes=0-3'.format(cpu_id, port_num)).readlines()
        results = ''.join(raw_results) 
        if 'Querying' not in results:
                success_time += 1
                time.sleep(2)
        else:
            print('AMDXIO Tool Failed! ({0},{1}), wait for 60 secs to retry'.format(cpu_id,port_num))
            fail_set_list = [cpu_id, port_num]
            fail_set = ','.join(fail_set_list)
            if fail_set not in failed_port:
                failed_port.append(fail_set)
            strs = ' '.join(failed_port)
            os.system("echo '{0}' > retry_ports.txt".format(strs))
            time.sleep(60)
    print('({0},{1}) complete! '.format(cpu_id, port_num))
    os.system("echo '({0}, {1})' >> complete.txt".format(cpu_id, port_num))           
    return


def get_cpu_mapping():
    cpu_mapping = {}
    for cpu_id in ('2','3'):
        cpu_port_num_list = os.popen("./AMDX -i={0} -listport | grep -E 'Port Num.*x4.*4'| cut -d ' ' -f 4".format(cpu_id)).readlines()
        if cpu_port_num_list:
            cpu_port_num_list = [str(x.strip('\n')) for x in cpu_port_num_list]    
            cpu_mapping[cpu_id] = cpu_port_num_list
    return cpu_mapping

def bus_scan():
    pass


# ------ Danger ------ #
os.system('echo>complete.txt')
os.system('echo>retry_ports.txt')
os.system('echo>TOOL.LOG')
cpu_mapping = get_cpu_mapping()
nvme_speed_normal_count = 0
#for k,v in cpu_mapping.items():
#    nvme_speed_normal_count += len(v)
#if nvme_speed_normal_count < 24:
#    error_count = 24 - nvme_speed_normal_count
#    print("{0} SSD Speed Abnormal (Not in Gen4 * Lane4 Mode, Please check!)")
#    exit()
#else:
#    print("24 SSD Speed is Gen4 * Lane4\nStarting SI Test...")
#    time.sleep(30)

#for cpu_id in cpu_mapping.keys():
#    port_num_list = cpu_mapping[cpu_id]
#    for port in port_num_list:
#        t = threading.Thread(target=get_single_si_result, args=(cpu_id, port))
#        time.sleep(1)
#        t.start()        
#    time.sleep(650)
get_single_si_result(2,4,5)


