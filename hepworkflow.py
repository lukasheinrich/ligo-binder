import adage
from adage import adagetask

@adagetask
def preparegrid(workdir, beamenergy, pol1, pol2):
    #prepare run card
    from string import Template
    with open('input/run_card.templ') as f:
        t = Template(f.read()).substitute(
            gridpack = True,
            nevents = 1,
            seed = 1234,
            sqrts_half = beamenergy,
            polbeam1 = pol1,
            polbeam2 = pol2,
        )
        runcardfilename = '{}/run_card.dat'.format(workdir)
        with open(runcardfilename,'w') as runcard:
            runcard.write(t)
            
    #prepare steering file
    steeringfilename = '{}/steer.dat'.format(workdir)
    with open(steeringfilename,'w') as steeringfile:
        steeringfile.write(
'''
import model sm
generate e+ e- > mu+ mu-
output {output}
launch -n output
{runcard}
quit
'''.format(
        output = '{}/gridpack'.format(workdir),
        runcard = runcardfilename,
            )
        )
    import subprocess
    subprocess.check_call(['mg5','-f',steeringfilename])
    
        
@adagetask
def generate(workdir,genworkdir,seed,nevents):
    os.makedirs(genworkdir)
    gridpackfile = '{}/gridpack/output_gridpack.tar.gz'.format(workdir)
    import tarfile
    t = tarfile.open(gridpackfile)
    t.extractall(path = genworkdir)
    import subprocess
    import shlex
    subprocess.check_call(shlex.split('./run.sh {} {}'.format(nevents,seed)), cwd = genworkdir)

@adagetask
def merge(workdir,genworkdirs):
    infiles = ['{}/events.lhe.gz'.format(x) for x in genworkdirs]
    import jsonlines
    import pylhe
    import gzip
    outfile = '{}/merged.jsonl'.format(workdir)
    with jsonlines.open(outfile,'w') as writer:
        for f in infiles:
            for e in pylhe.readLHE(gzip.open(f)):
                writer.write(e)

import os
import shutil
def setup_workflow(workdir = 'workdir', nevents = 40000, beamenergy = 45.0, pol1 = 100, pol2 = -100):

    workdir = workdir

    if os.path.exists(workdir):
        shutil.rmtree(workdir)
    os.makedirs(workdir)
    
    seeds = [1,2,3,4]
    workflow = adage.adageobject()

    n_prepgrid = workflow.dag.addTask(preparegrid.s(
            workdir = workdir,
            beamenergy = beamenergy,
            pol1 = pol1,
            pol2 = pol2
        ),
        nodename = 'prepare'
    )

    evgen_nodes = []
    genworkdirs = []
    for i,x in enumerate(seeds):
        genworkdir = '{}/gen_{}'.format(workdir,i)
        genworkdirs.append(genworkdir)
        evgen_nodes.append(
            workflow.dag.addTask(generate.s(
                    workdir = workdir,
                    seed = x,
                    genworkdir = genworkdir,
                    nevents = nevents/len(seeds)
                    ),
                depends_on = [n_prepgrid], nodename = 'generate')
        )

    n_merge = workflow.dag.addTask(merge.s(workdir = workdir,genworkdirs = genworkdirs), depends_on = evgen_nodes, nodename = 'merge')
    return workflow
