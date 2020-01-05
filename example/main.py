from blackswan_client.main import BlackSwanAPI

if __name__ == "__main__":
    blkswan = BlackSwanAPI(0.05, 200)
    blkswan.connect('root', 'root', 'blackswan_dev', 'scruffy.soe.ucsc.edu')
    print(blkswan.get_no_of_reps_for_cpu_st('SP', 'yes', 0, 'mops_total'))
    print(blkswan.get_no_of_reps_for_cpu_mt('SP', 'yes', 0, 'mops_total'))
    print(blkswan.get_no_reps_for_membench('yes', 0, 'read_memory_avx_max'))
    print(blkswan.get_no_reps_for_stream('yes', 0, 'triad_stdev'))
    print(blkswan.no_of_reps_for_fio(4096, 'read_rand', 'sda4', 'READ_IOPS'))
    print(blkswan.get_machines({ "blockdevices": "nvme0n1" }))
    print(blkswan.get_machine_ids({ "blockdevices": "nvme0n1" }))
