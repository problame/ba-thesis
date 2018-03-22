#!/usr/bin/env python3
from pathlib import Path
import subprocess
import json
import os
import sys


TEMPLATE="""
worker: {worker}

mysqlcommand : {mysql_command}
perfcommand: {perf_command}

tpcc:
    seconds: {tpcc_secs}
    terminals: {tpcc_terminals}
    scalefactor: 2
    mysql:
        host: {mysql_host}
        port: 3306
        user: root
        password: ""
        db: tpcc
"""

doltp_bin = "./ba-doltp"
blobsdir = Path("../../blobs/whole_system")
datadir = None # set in __main__
core_range = "2-7"
skipexisting = False

tpcc_secs = 10
iterations = 4

perf_command = json.dumps([ "./perf.sh",
                            "ref-cycles cpu_clk_unhalted.thread idq_uops_not_delivered.core uops_issued.any uops_retired.retire_slots int_misc.recovery_cycles l2_rqsts.all_code_rd l2_rqsts.code_rd_miss l2_rqsts.miss l2_rqsts.references",
                            "ukHG",
                            core_range
                          ])

perf_nullcmd = json.dumps(["bash", "-c", "sleep 30d"])

def do_iterations(name, conf_args):
    conf = TEMPLATE.format(**conf_args)
    for i in range(0, iterations):
        resultdir = datadir / (name + '_{}'.format(i))
        if skipexisting and os.path.exists(resultdir):
            print("INFO: skipping existing result dir: {}".format(os.path.basename(resultdir)))
            continue
        conffile = ".doltp.conf.tmp"
        with open(conffile, "w") as c:
            c.write(conf)
        subprocess.check_call([doltp_bin, "controller", "--config", conffile, "--result", resultdir], timeout=tpcc_secs+120)
        with open(Path(resultdir) / 'params.json', 'w') as pf:
            json.dump(conf_args, pf, indent=1)

def do_osv_iterations(name, osv_img, tpcc_terminals, osv_cmdline="", perf=True):

    mysql_command = [ "./osv.sh", str(osv_img), core_range, str(osv_cmdline) ]
    pc = perf_command if perf else perf_nullcmd
    args = {
        'core_range':core_range,
        'mysql_command':json.dumps(mysql_command),
        'worker' : '10.23.42.40:22345',
        "tpcc_terminals":tpcc_terminals,
        "tpcc_secs":tpcc_secs,
        "mysql_host":"10.23.42.10",
        "perf_command": pc,
    }
    do_iterations(name, args)

def do_linuxvm_iterations(name, tpcc_terminals, perf=True):
    mysql_command = [ "./linuxvm.sh", str(blobsdir / 'linuxvm.img'), core_range ]
    pc = perf_command if perf else perf_nullcmd
    args = {
        'core_range':core_range,
        'mysql_command':json.dumps(mysql_command),
        'worker' : '10.23.42.40:22345',
        "tpcc_terminals":tpcc_terminals,
        "tpcc_secs":tpcc_secs,
        "mysql_host":"10.23.42.10",
        "perf_command":pc,
    }
    do_iterations(name, args)

if __name__ == "__main__":

    abspath = os.path.abspath(__file__)
    if len(sys.argv) != 2:
        print("usage: {} OUTPUTDIR".format(os.path.basename(abspath)))
        sys.exit(1)
    datadir = Path(os.path.abspath(sys.argv[1]))

    os.chdir(os.path.dirname(abspath))

    tpcc_secs = 40
    threads = [1,2, 6, 10, 15, 20, 25, 30, 40, 50, 60]
    iterations = 8
    skipexisting = True
    for t in threads:
        for maa in [i*(10**6) for i in [1,5,10,20,50,100]]:
            for mwait in [0, 1]:
                itname = "devMAA_mine_t{}_mwait{}_maa{}".format(t,mwait,maa)
                do_osv_iterations(itname, blobsdir / 'dev_eval_v0.24-530-gcf16063b.img', t, "--stage.max_assignment_age={} --idle_mwait={}".format(maa, mwait))

    for t in threads:
        for nospin in [ 0, 1 ]:
            for ies in [ 0, 1, 2]:
                allowed = [ (0,1), (1,2), (0,0), (0,2) ]
                if not (nospin, ies) in allowed:
                    continue
                do_osv_iterations("upstream_t{}_nospin{}_ies{}".format(t,nospin,ies), blobsdir / 'upstream_eval_base_v0.24-471-g3ba2daa5.img', t, "--idle_nospin={nospin} --idle_empty_strategy={ies}".format(nospin=nospin, ies=ies))


    for t in threads:
        for fixed in [1, 2]:
            #for maa in [i*(10**6) for i in [1,5,10,20,50,100]]: doesnot make a difference, it's fixed
            for mwait in [0, 1]:
                itname = "mineFixed{}C_t{}_mwait{}".format(fixed, t, mwait, maa)
                do_osv_iterations(itname, blobsdir / 'dev_eval_v0.24-530-gcf16063b.imgg', t, "--stage.fixed_cpus_per_stage={} --idle_mwait={}".format(fixed, mwait))

    for t in threads:
        do_linuxvm_iterations("linuxvm_t{}".format(t), t)

    for t in [1,6,30, 10, 15, 40, 60, 50, 20]:
        for maa in [i*(10**6) for i in [1,5,10,20,50,100]]:
            for mwait in [0, 1]:
                itname = "mine_cinrunq2_t{}_mwait{}_maa{}".format(t,mwait,maa)
                do_osv_iterations(itname, blobsdir / 'mine_cinrunq2_v0.24-532-gb177c65f.img', t, "--stage.max_assignment_age={} --idle_mwait={}".format(maa, mwait))

    for t in threads:
        for maa in [i*(10**6) for i in [10,20,50]]:
            for mwait in [0, 1]:
                itname = "mine_cinrunq3_t{}_mwait{}_maa{}".format(t,mwait,maa)
                do_osv_iterations(itname, blobsdir / 'mine_cinrunq3_v0.24-533-g1d3b2595.img', t, "--stage.max_assignment_age={} --idle_mwait={}".format(maa, mwait))

    # noperf runs
    for t in threads:
       do_linuxvm_iterations("noperf_linuxvm_t{}".format(t), t, perf=False)
       for nospin,ies in [ (0,1),(0, 0) ]:
           for ies in [ 1 ]:
               do_osv_iterations("noperf_upstream_t{}_nospin{}_ies{}".format(t,nospin,ies), blobsdir / 'upstream_eval_base_v0.24-471-g3ba2daa5.img', t, "--idle_nospin={nospin} --idle_empty_strategy={ies}".format(nospin=nospin, ies=ies), perf=False)
    for t in threads:
       for maa in [i*(10**6) for i in [20]]:
           for mwait in [0, 1]:
               itname = "noperf_mine_cinrunq3_t{}_mwait{}_maa{}".format(t,mwait,maa)
               do_osv_iterations(itname, blobsdir / 'mine_cinrunq3_v0.24-533-g1d3b2595.img', t, "--stage.max_assignment_age={} --idle_mwait={}".format(maa, mwait), perf=False)

    for t in threads:
        for nospin in [ 0, 1 ]:
            for ies in [ 0, 1, 2]:
                allowed = [ (0,1), (0,0), (1,2), (0,2) ]
                if not (nospin, ies) in allowed:
                    continue
                do_osv_iterations("upstreamFixed2C_t{}_nospin{}_ies{}".format(t,nospin,ies), blobsdir / 'upstream_eval_base_threadmig_b0575125.img', t, "--stage.fixed_cpus_per_stage=2 --idle_nospin={nospin} --idle_empty_strategy={ies}".format(nospin=nospin, ies=ies))


