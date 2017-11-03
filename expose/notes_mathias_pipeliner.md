

* Thread migration using `sched_setaffinity` is too expensive
    * boils down to IPIs used under the hood
    * -> chatlog has times
    * -> cannot just migrate linux tasks (KLTs) between CPUs using this technique

* Hybrid Implementation
    * assume: one KLT per core & stage (`#core >= #stage`)
    * TLS (selfbuild, using gs segment register(?))
        * why selfbuilt? because other code might want to use `thread_local` storage class (C++11)
    * Terminology:
        * ULT: a thread from the perspective of the userspace application
        * KLT: a thread from the perspective of the linux kernel
        * -> ULTs live on different KLTs, depending on which stage they are in
        * -> KLTs are pinned to a CPU using sched_setaffinity

    * queue of ThreadState kept in Scheduler
    * ThreadPool creates and manages KLTs
    * A KLT asks Scheduler for ULTContext and switchtes to it
    * How does the Scheduler find ULTContext
        * SYS_pipeliner_wait to get a partition index
            * OBSERVE: the kernel determines which partition a KLT is executing
        * Use atomic instructions to dequeue from a list of ready ULTContexts
* Problem
    * Scenario 1
        * ULT U1 running on a KLT K1 does a syscall
        * that syscall causes K1 to change state to TASK_INTERRUPTIBLE (S in ps(8))
        * NOTE(1) that ThreadPool / Scheduler did _not_ observe that U1 / K1 went to sleep
            * from their perspective, U1 is executing
            * they cannot distinguish between user \& kernel code
        * The Linux scheduler picks another task K2 to run on the core K1 was pinned to
            * Note this could be any task, not even in the same app
        * Callback from kernel/scheduler/core.c to kernel/pipeliner.c (pipeliner_on_start_running())
            * K1 is TASK_RUNNING again, but pinned to the same core as K2
            * Thus K1 is not scheduled immediately
            * Let's assume there is another eligible core + KLT K3 for U1's current stage
                * It is in SYS_pipeliner_wait, waiting for work
            * IDEAL:
                * Immediately schedule U1 on K3
            * REAL due to implementation (see NOTE(1))
                * Thread migration is implemented in ThreadPool
                * ThreadPool for U1 / K1 will not run until U1 calls into ThreadPool code (pipline switch, etc)
                * Thus, even though K3 was available to execute U1, U1 only resumes when K1 resumes, and K3 stays idle

