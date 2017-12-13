import bisect

class SchedulerOptimal():
    # FIXME need to be able to return the whole optimal schedule not just reward
    def evaluate(self, job_sequences, num_sequences, num_machines):
        opt_rewards = []
        for _ in range(num_sequences):
            job_sequence = next(job_sequences)

            if num_machines == 1:
                opt_reward = self._schedule_one_machine(job_sequence)
            elif num_machines == 2:
                opt_reward = self._schedule_two_machines(job_sequnce)
            else:
                opt_reward = self._schedule_mult_machines(job_sequence)

            opt_rewards.append(opt_reward)

        return opt_rewards

    def _sort_jobs(self, jobs):
        return sorted(jobs, key=lambda x: x.departure)

    def _calculate_latest_previous_job(self, sorted_jobs):
        prev = [0 for i in range(len(sorted_jobs))]
        departures = [job.departure for job in sorted_jobs]
        for i, job in enumerate(sorted_jobs):
            prev[i] = bisect.bisect_right(departures, job.arrival)

        return prev

    # TODO need to return the optimal schedule
    def _schedule_one_machine(self, jobs):
        opt = [0 for i in range(len(jobs) + 1)]
        sorted_jobs = self._sort_jobs(jobs)
        prev = self._calculate_latest_previous_job(sorted_jobs)
        for i, job in enumerate(sorted_jobs):
            opt[i+1] = max(job.value + opt[prev[i]], opt[i])

        return opt[-1]

    def _schedule_two_machines(self, jobs):
        pass
       
    def _schedule_mult_machines(self, jobs):
        pass


