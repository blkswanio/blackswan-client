from blackswan_client.main import BlackSwanAPI

if __name__ == "__main__":
    blkswan = BlackSwanAPI()
    blkswan.connect('root', 'root', 'blackswan3', 'scruffy.soe.ucsc.edu')
    blkswan.set_allowed_err_and_trial_cnt(0.05, 200)
    print(blkswan.get_no_of_reps(
    machine_predicate = {
        "architecture": "amd64"
    },
    benchmark_predicate = { 
    }, param = 'READ_IOPS', test = 'fio'))