'''
Reading the RAMSES log files of a run directory.

A run directory is holds one run_*.log per repeat. Every log starts with the header written by
the launcher (key: value lines between two lines of #), followed by the header of
RAMSES (compile command, last commit, ...), and ends with the timers.
'''


''' Value of a "Used memory" line in MB, from its unit. '''
def memory_in_mb(value, unit):
    value = float(value)
    if unit=='kB':
        value = value/1e3
    elif unit=='GB':
        value = value*1e3
    elif unit=='TB':
        value = value*1e6
    return value


''' Read a log in a single pass. Returns a dict with
      meta:   the key: value lines of the header written by the launcher (between
              the first two lines of #), and the compile command from the header
              written by RAMSES (read until "last commit", at most 100 lines after
              the launcher header)
      total:  the total time (first column of the TOTAL line), None if the run
              did not finish
      timers: {name: time} of the lines between TIMER and TOTAL: average time in
              the second column, name from column 91 (e.g. 'poisson - phi multigrid').
              The name has a fixed position because the columns before it can run
              together (rank numbers of 4 digits or more).
      memory: the largest "Used memory" in the log, in MB (the largest value over
              the ranks at every step), None if not found '''
def read_log(logfile):
    meta = {}
    totals = []
    timers = {}
    memory = None

    # header: before / inside the launcher block, then the RAMSES header
    start_meta = False
    end_meta = False
    header_done = False
    nlines_header = 0
    in_timers = False

    with open(logfile, 'r') as f:
        for line in f:
            if not header_done:
                if (not start_meta) and line.startswith("##################"):
                    start_meta = True
                elif start_meta and (not end_meta):
                    if line.startswith("##################"):
                        end_meta = True
                    else:
                        try:
                            [key, value] = line.strip().split(': ')
                            meta[key] = value
                        except ValueError:
                            pass
                else:
                    stripped = line.strip()
                    if stripped.startswith('compile command'):
                        meta['compile command'] = stripped.split('=', 1)[1].strip()
                    elif stripped.startswith('last commit'):
                        header_done = True
                    if not header_done:
                        nlines_header += 1
                        if nlines_header > 100:
                            header_done = True

            if 'Used memory' in line:
                value, unit = line.split()[2:4]
                mem = memory_in_mb(value, unit)
                memory = mem if memory is None else max(memory, mem)

            # every line containing TOTAL (as grep TOTAL)
            if 'TOTAL' in line:
                totals.append(float(line.split()[0]))
            # lines between TIMER and TOTAL (as awk '/TIMER/{flag=1; next}/TOTAL/{flag=0} flag')
            if 'TIMER' in line:
                in_timers = True
                continue
            if 'TOTAL' in line:
                in_timers = False
            if in_timers:
                timers[line[90:].strip()] = float(line.split()[1])

    # a finished run prints a single TOTAL line
    if len(totals)>1:
        print(f'WARNING: {len(totals)} TOTAL lines in {logfile}, the last one is used')
    return {'meta': meta, 'total': totals[-1] if totals else None, 'timers': timers, 'memory': memory}
