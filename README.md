4D-GRAPHS-prototype
=========

4D-GRAPHS-prototype is software for automated all-atom resonances assignment from a single 4D HCNH NOESY spectrum.

License
============

4D-GRAPHS-prototype software for protein NMR assignment is a property of **Masaryk university** and the authors are **Thomas Evangelidis**, **Tomas Brazdil**, **Jiri Filipovic** and **Konstantinos Tripsianes**. The code is licensed under the Attribution-NonCommercial-NoDerivatives 4.0 International (CC BY- NC-ND 4.0). You are free to:

* Share - copy and redistribute the material in any medium or format.
* The licensor cannot revoke these freedoms as long as you follow the license terms.

Under the following terms:

* Attribution - You must give appropriate credit, provide a link to the license, and indicate if changes were made. You may do so in any reasonable manner, but not in any 		  way that suggests the licensor endorses you or your use.
* NonCommercial - You may not use the material for commercial purposes.
* NoDerivatives - If you remix, transform, or build upon the material, you may not distribute the modified material.
* No additional restrictions - You may not apply legal terms or technological measures that legally restrict others from doing anything the license permits.
To view a full copy of this license, visit [this page](https://creativecommons.org/licenses/by-nc-nd/4.0/legalcode).

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
* Do this every time you wish to run 4D-GRAPHS-prototype.
* Getting code and data
  - `git clone https://github.com/4D-GRAPHS/4D-GRAPHS-prototype.git`
  - `cd 4D-GRAPHS-prototype`
  - `wget http://4d-graphs.cerit-sc.cz/models.zip`
  - `unzip models.zip`
  - `cd graph_alg`
  - `make`
  - `cd ..`

Execution
---------
The 4D-graphs-prototype is distributed with an example protein 3NIK, stored in input/3NIK (raw data) and input/3NIK-curated (annotated data). The 4D-graphs-prototype is executed by the following command:
* `python3 EXEC_master_NOESY.py -p 3NIK-curated`

which uses the 3NIK-curated protein. The result is stored into output_NHmapping.csv file. Note that precision of the result on 3NIK can be improved by changing method of graph edge weight computation by changing value of `what_edge_weight` to `EdgeWeightType.intersections` in `NOESY_master_settings.py`. This method is available for 3NIK-curated protein only with curent implementation, its universal implementation appears in 4D-GRAPHS-prototype soon.

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

With the new protein ‘prot’ stored in input/prot, the 4D-graphs-prototype can be executed by the command:
 * `python3 EXEC_master_NOESY.py -p prot`
