import os
import platform
import psutil
import socket
import time
from module_admin.entity.vo.server_vo import CpuInfo, MemoryInfo, PyInfo, ServerMonitorModel, SysFiles, SysInfo
from utils.common_util import bytes2human
from utils.log_util import logger


class ServerService:
    """
    服务监控模块服务层
    """

    @staticmethod
    async def get_server_monitor_info():
        try:
            # CPU信息
            try:
                cpu_num = psutil.cpu_count(logical=True)
                cpu_usage_percent = psutil.cpu_times_percent()
                cpu_used = cpu_usage_percent.user
                cpu_sys = cpu_usage_percent.system
                cpu_free = cpu_usage_percent.idle
                cpu = CpuInfo(cpuNum=cpu_num, used=cpu_used, sys=cpu_sys, free=cpu_free)
            except Exception as e:
                logger.warning(f'获取CPU信息失败: {e}')
                cpu = CpuInfo(cpuNum=0, used=0, sys=0, free=0)

            # 内存信息
            try:
                memory_info = psutil.virtual_memory()
                memory_total = bytes2human(memory_info.total)
                memory_used = bytes2human(memory_info.used)
                memory_free = bytes2human(memory_info.free)
                memory_usage = memory_info.percent
                mem = MemoryInfo(total=memory_total, used=memory_used, free=memory_free, usage=memory_usage)
            except Exception as e:
                logger.warning(f'获取内存信息失败: {e}')
                mem = MemoryInfo(total='0B', used='0B', free='0B', usage=0)

            # 主机信息
            try:
                hostname = socket.gethostname()
                # 安全获取IP地址
                try:
                    computer_ip = socket.gethostbyname(hostname)
                except socket.gaierror:
                    computer_ip = '127.0.0.1'
                except Exception:
                    computer_ip = '127.0.0.1'
                
                os_name = platform.platform()
                computer_name = platform.node()
                os_arch = platform.machine()
                user_dir = os.path.abspath(os.getcwd())
                sys = SysInfo(
                    computerIp=computer_ip, computerName=computer_name, osArch=os_arch, osName=os_name, userDir=user_dir
                )
            except Exception as e:
                logger.warning(f'获取主机信息失败: {e}')
                sys = SysInfo(
                    computerIp='127.0.0.1', computerName='Unknown', osArch='Unknown', osName='Unknown', userDir='Unknown'
                )

            # python解释器信息
            try:
                current_pid = os.getpid()
                current_process = psutil.Process(current_pid)
                python_name = current_process.name()
                python_version = platform.python_version()
                python_home = current_process.exe()
                start_time_stamp = current_process.create_time()
                start_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time_stamp))
                current_time_stamp = time.time()
                difference = current_time_stamp - start_time_stamp
                # 将时间差转换为天、小时和分钟数
                days = int(difference // (24 * 60 * 60))  # 每天的秒数
                hours = int((difference % (24 * 60 * 60)) // (60 * 60))  # 每小时的秒数
                minutes = int((difference % (60 * 60)) // 60)  # 每分钟的秒数
                run_time = f'{days}天{hours}小时{minutes}分钟'
                
                # 获取该进程的内存信息
                current_process_memory_info = current_process.memory_info()
                py = PyInfo(
                    name=python_name,
                    version=python_version,
                    startTime=start_time,
                    runTime=run_time,
                    home=python_home,
                    total=bytes2human(memory_info.available),
                    used=bytes2human(current_process_memory_info.rss),
                    free=bytes2human(memory_info.available - current_process_memory_info.rss),
                    usage=round((current_process_memory_info.rss / memory_info.available) * 100, 2),
                )
            except Exception as e:
                logger.warning(f'获取Python信息失败: {e}')
                py = PyInfo(
                    name='Unknown', version='Unknown', startTime='Unknown', runTime='Unknown', 
                    home='Unknown', total='0B', used='0B', free='0B', usage=0
                )

            # 磁盘信息
            try:
                io = psutil.disk_partitions()
                sys_files = []
                for i in io:
                    try:
                        o = psutil.disk_usage(i.device)
                        disk_data = SysFiles(
                            dirName=i.device,
                            sysTypeName=i.fstype or 'Unknown',
                            typeName='本地固定磁盘（' + i.mountpoint.replace('\\', '') + '）',
                            total=bytes2human(o.total),
                            used=bytes2human(o.used),
                            free=bytes2human(o.free),
                            usage=f'{o.percent}%',
                        )
                        sys_files.append(disk_data)
                    except Exception as e:
                        logger.warning(f'获取磁盘分区信息失败: {i.device}, 错误: {e}')
                        continue
            except Exception as e:
                logger.warning(f'获取磁盘信息失败: {e}')
                sys_files = []

            result = ServerMonitorModel(cpu=cpu, mem=mem, sys=sys, py=py, sysFiles=sys_files)
            return result
            
        except Exception as e:
            logger.error(f'获取服务器监控信息失败: {e}')
            # 返回默认值，避免500错误
            default_cpu = CpuInfo(cpuNum=0, used=0, sys=0, free=0)
            default_mem = MemoryInfo(total='0B', used='0B', free='0B', usage=0)
            default_sys = SysInfo(
                computerIp='127.0.0.1', computerName='Unknown', osArch='Unknown', osName='Unknown', userDir='Unknown'
            )
            default_py = PyInfo(
                name='Unknown', version='Unknown', startTime='Unknown', runTime='Unknown', 
                home='Unknown', total='0B', used='0B', free='0B', usage=0
            )
            return ServerMonitorModel(
                cpu=default_cpu, mem=default_mem, sys=default_sys, py=default_py, sysFiles=[]
            )
