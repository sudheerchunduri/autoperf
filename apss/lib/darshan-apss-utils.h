#ifndef __APSS_UTILS_H__
#define __APSS_UTILS_H__

#include <regex.h>
extern char crusher_nodelist[192][14];
static void search_hwinfo(const char * mstr, char *mode)
{
    FILE *f;
    int r;
    char *fdata;
    long len;
    regex_t preg;
    regmatch_t mreg[1];

    r = regcomp(&preg, mstr, 0);

    f = fopen ("/.hwinfo.cray", "rb");
    fseek(f, 0, SEEK_END);
    len = ftell(f);
    fdata = malloc(len);
    fseek(f, 0, SEEK_SET);
    fread(fdata, sizeof(char), len, f);
    fclose(f);

    r = regexec(&preg, fdata, 1, mreg, 0);
    if ((r == 0) && (mreg[0].rm_so > -1))
    {
        sscanf(fdata+mreg[0].rm_so+strlen(mstr)-2, "%s", mode);
    }
    regfree(&preg);
    free(fdata);

    return;
}

static int sstopo_get_mycoords(int* group, int* chassis, int* slot, int* blade, int* node)
{
   char hostname[HOST_NAME_MAX + 1];
    gethostname(hostname, HOST_NAME_MAX + 1);

    char a, b, c, d, e;
    int layer_temp;
    int rack;
    /* format example: c1-0c1s2n1 c3-0c2s15n3 */
    /* format example: x3012c0s13b0n0 */
    sscanf(crusher_nodelist[atoi(hostname+7)],
           "%c%d%c%d%c%d%c%d%c%d",
           &a, &rack, &b, chassis, &c, slot, &d, blade, &e, node);

    if(rack == 2601){
            *group = 0;
    }
    else{
            *group = 1;
    }
#ifdef DEBUG
    fprintf(stderr, "coords = (%d,%d, %d, %d,%d,%d,%d) \n", layer_rank, blade_rank, node_rank, *group, *chassis, *slot, *blade, *node);
#endif

  return 0;
}

static unsigned int count_bits(unsigned int *bitvec, int cnt)
{
    unsigned int count = 0;
    int i;

    for (i = 0; i < cnt; i++)
    {
        count += __builtin_popcount(bitvec[i]);
    }
    return count;
}

#endif
