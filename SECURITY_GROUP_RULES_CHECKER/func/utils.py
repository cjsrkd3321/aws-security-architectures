import ipaddress

from multiprocessing import Process
from concurrent.futures import ThreadPoolExecutor


protocols = {"tcp": "6", "udp": "17"}


def run_multi_processes(func, service, iterables):
    processes = []
    for iterable in iterables:
        process = Process(
            target=func,
            args=(
                service,
                iterable,
            ),
        )
        processes.append(process)

    # start all processes
    for process in processes:
        process.start()

    # make sure that all processes have finished
    for process in processes:
        process.join()


def get_results_using_multi_threads(func, iterables, max_workers=10):
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results += executor.map(func, iterables)
    return results


def combine_ports(from_port, to_port):
    if from_port == to_port:
        return [from_port]
    return range(from_port, to_port + 1)


def is_included_port(port, dst_ports):
    if port == "ALL" or int(port) in dst_ports:
        return True
    return False


def is_equal_protocol(proto_num, protocol):
    global protocols
    if protocol == "-1" or proto_num == protocols[protocol]:
        return True
    return False


def is_included_ip(log_ip, target_ips):
    for target_ip in target_ips:
        if ipaddress.ip_address(log_ip) in ipaddress.ip_network(target_ip):
            return True
    return False
