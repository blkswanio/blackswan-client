from baseliner import Baseliner

if __name__ == "__main__":
    baseliner = Baseliner()
    baseliner.connect('root', 'root', 'blackswan3', 'scruffy.soe.ucsc.edu')
    baseliner.set_allowed_err_and_trial_cnt(0.05, 200)
    print(baseliner.get_no_of_reps(
        machine_predicate={
            "architecture": "amd64"
        },
        benchmark_predicate={
        }, param='READ_IOPS', test='fio'))
