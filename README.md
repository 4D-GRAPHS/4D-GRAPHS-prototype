4D-GRAPHS
=========

4D-GRAPHS is software for automated all-atom resonances assignment from a single 4D HCNH NOESY spectrum.

Installation
------------
* Prerequisites:
  - python 3.6.9
  - pandas 1.1.5
  - sklearn 0.23.1
  - pretty-errors 1.2.19
  - g++ 4.7
  - make
* Python dependencies can be easily installed by creating an Anaconda Python environment from the provided 4dgraphs.yml file:
  - `conda env create -f 4dgraphs.yml`
* Activate the new environment: 
  - `conda activate 4dgraphs`
* Do this every time you wish to run 4D-GRAPHS.
* Getting code and data
  - `git clone https://github.com/4D-GRAPHS/4D-GRAPHS.git`
  - `cd 4D-GRAPHS`
  - `wget http://4d-graphs.cerit-sc.cz/models.zip`
  - `unzip models.zip`
  - `cd graph_alg`
  - `make`
  - `cd ..`

Execution
---------
The 4D-graphs is distributed with an example protein 3NIK, stored in input/3NIK (raw data) and input/3NIK-curated (annotated data). The 4D-graphs is executed by the following command:
* `python3 EXEC_master_NOESY.py -p 3NIK-curated`

which uses the 3NIK-curated protein. The result is stored into output_NHmapping.csv file. Note that precision of the result on 3NIK can be improved by changing method of graph edge weight computation by changing value of `what_edge_weight` to `EdgeWeightType.intersections` in `NOESY_master_settings.py`. This method is available for 3NIK-curated protein only with curent implementation, the universal method will be implemented in 4D-GRAPHS soon.

Running with own data
---------------------
New proteins have to be placed into their own folders in input/. The protein ‘prot’, stored in folder input/prot, have to contain:
 * FASTA file `prot.fasta` containing the protein sequence
 * list of HCNH peaks in `prot_HCNH.list` file
 * list of HSQC peaks in `prot_HSQC.list` file
 * optionally list of HNNH peaks in `prot_HNNH.list` file

The peaks lists contain the following column:
 * the assignment of the HCNH group (‘?-?-?-?’ when unknown)
 * position of the peak in each dimension (4 for HCNH and HNNH, 2 for HSQC)
 * the amplitude of the peak (only HCNH and HNNH lists)

With the new protein ‘prot’ stored in input/prot, the 4D-graphs can be executed by the command:
 * `python3 EXEC_master_NOESY.py -p prot`
