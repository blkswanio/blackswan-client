from blackswan_client.main import BlackSwanAPI

if __name__ == "__main__":
    blkswan = BlackSwanAPI(0.05, 200)
    blkswan.connect('root', 'root', 'blackswan_dev', 'scruffy.soe.ucsc.edu')
    print(blkswan.get_machine_details({ "blockdevices": "nvme0n1" }))
    print(blkswan.get_machine_ids({ "blockdevices": "nvme0n1" }))
    print(blkswan.get_no_of_reps(
    machine_predicate = {
        "blockdevices": "nvme0n1"
    }, 
    benchmark_predicate = { 
        "testname": "SP",
        "dvfs": "yes",
        "socket": 0
     }, param = 'mops_total', test = 'npb_cpu_mt'))