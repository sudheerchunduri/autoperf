import cffi
import ctypes

import numpy as np
import darshan.backend.cffi_backend

# APMPI structure defs
structdefs = '''
struct darshan_apmpi_perf_record
{
    struct darshan_base_record base_rec;
    uint64_t counters[364];
    double fcounters[168];
    double fsynccounters[16];
    double fglobalcounters[2];
};
struct darshan_apmpi_header_record
{
    struct darshan_base_record base_rec;
    int64_t magic;
    double apmpi_f_variance_total_mpitime;
    double apmpi_f_variance_total_mpisynctime;
};

extern char *apmpi_counter_names[];
extern char *apmpi_f_mpiop_totaltime_counter_names[]; 
extern char *apmpi_f_mpiop_synctime_counter_names[];
extern char *apmpi_f_mpi_global_counter_names[];

'''

def get_apmpi_defs():
  return structdefs


# load header record
def log_get_apmpi_record(log, dtype='dict'):
    from darshan.backend.cffi_backend import ffi, libdutil, log_get_modules, counter_names

    mod_name = 'APMPI'
    modules = log_get_modules(log)


    rec = {}
    buf = ffi.new("void **")
    r = libdutil.darshan_log_get_record(log['handle'], modules[mod_name]['idx'], buf)
    if r < 1:
        return None

    hdr = ffi.cast('struct darshan_apmpi_header_record **', buf)
    prf = ffi.cast('struct darshan_apmpi_perf_record **', buf)

    rec['id'] = hdr[0].base_rec.id
    rec['rank'] = hdr[0].base_rec.rank

    if hdr[0].magic == 280520118345:
      rec['magic'] = hdr[0].magic
      rec['variance_total_mpitime'] = hdr[0].apmpi_f_variance_total_mpitime
      rec['variance_total_mpisynctime'] = hdr[0].apmpi_f_variance_total_mpisynctime
    else:

      lst = []
      for i in range(0, len(prf[0].counters)):
        lst.append(prf[0].counters[i])
        np_counters = np.array(lst, dtype=np.uint64)
        d_counters = dict(zip(counter_names(mod_name), np_counters))

      lst = []
      for i in range(0, len(prf[0].fcounters)):
        lst.append(prf[0].fcounters[i])
        np_fcounters = np.array(lst, dtype=np.float64)
        d_fcounters = dict(zip(counter_names(mod_name, fcnts=True, special='mpiop_totaltime_'), np_fcounters))

      lst = []
      for i in range(0, len(prf[0].fsynccounters)):
        lst.append(prf[0].fsynccounters[i])
        np_fsynccounters = np.array(lst, dtype=np.float64)
        d_fsynccounters = dict(zip(counter_names(mod_name, fcnts=True, special='mpiop_synctime_'), np_fsynccounters))

      lst = []
      for i in range(0, len(prf[0].fglobalcounters)):
        lst.append(prf[0].fglobalcounters[i])
        np_fglobalcounters = np.array(lst, dtype=np.float64)
        d_fglobalcounters = dict(zip(counter_names(mod_name, fcnts=True, special='mpi_global_'), np_fglobalcounters))

      if dtype == 'numpy':
        rec['counters'] = np_counters
        rec['fcounters'] = np_fcounters
        rec['fsynccounters'] = np_fsynccounters
        rec['fglobalcounters'] = np_fglobalcounters
      else:
        rec['counters'] = d_counters
        rec['fcounters'] = d_fcounters
        rec['fsynccounters'] = d_fsynccounters
        rec['fglobalcounters'] = d_fglobalcounters
    
    return rec
