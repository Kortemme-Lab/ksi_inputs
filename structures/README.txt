0. Get rid of the existing versions of the files we'll be generating::

      $ rm -rf 1qjg_*

1. Get rid of all the atoms we don't want and number everything consecutively::

      $ ./clean_1qjg.pdb

2. Relax the cleaned structure 100 times, using very tight constraints::

      $ ./qsub_relax_1qjg.sh  # on the cluster

3. Score all the relaxed structures, to make sure the simulations are converged 
   and the RMSDs are very small (about 0.1Å)::
      
      $ ./score_relaxed.sh

3. Pick the best-scoring relaxed structure::

      $ ./pick_relaxed.py

4. Repack that structure 100 times::

      $ ./qsub_repack_1qjg.sh

5. Score all the repacked structures, to make sure the simulations have 
   converged and the scores are better than before::

      $ ./score_repacked.sh

6. Pick the best-scoring repacked structure::

      $ ./pick_repacked.py

`1qjg_clean_relax_repack.pdb` is the relaxed structure that should be fed into 
the design pipeline.
