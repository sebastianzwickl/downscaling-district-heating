# Sequential and iterative downscaling algorithms

Copyright (c) 2021 Energy Economics Group (EEG), Technische Universität Wien, Sebastian Zwickl-Bernhard

[![MIT license](https://img.shields.io/badge/License-MIT-blue.svg)](https://lbesson.mit-license.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

This repository contains the underlying Python code of the paper *Disclosing heat density of centralized heat networks in Austria 2050 under the 1.5°C climate target*.
It has been developed during the *Young Scientist Summer Programme* (YSSP) at the Internatioanl Institute of Applied Systems Analysis (IIASA).

# # Overview

The main purpose of the Python code is downscaling heat generation by source from the country level to the municipal level. 
A small example for the Austrian sub-region *South Viennese environs* (AT127) is provided [here](downscaling\Iterative-downscaling-results).

# # How to use the scripts and replicate the small example?

1.	Execute 'run_seq_downscaling.py' downscaling heat generation by source from the country to the NUTS3 level.
2.	Execute 'run_iter_downscaling.py' downscaling centralized and decentralized heat generation from the NUTS3 level to the municipal (LAU) level.

## Acknowledgement

<img src="./_static/open_entrance-logo.png" width="202" height="129" align="right" alt="openENTRANCE logo" />

This package is based on the work initially done in the
[Horizon 2020 openENTRANCE](https://openentrance.eu) project, which aims to  develop,
use and disseminate an open, transparent and integrated  modelling platform
for assessing low-carbon transition pathways in Europe.

Refer to the [openENTRANCE/nomenclature](https://github.com/openENTRANCE/nomenclature)
repository for more information.

<img src="./_static/EU-logo-300x201.jpg" width="80" height="54" align="left" alt="EU logo" />
This project has received funding from the European Union’s Horizon 2020 research
and innovation programme under grant agreement No. 835896.
