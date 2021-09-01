import utils as u
from pyam import IamDataFrame

"""
Algorithm 1: Sequential downscaling algorithm (NUTS0 to NUTS3)

t: Heat generation technology/source (t in T)
r: Sub-region (or NUTS3 region) (r in R)

input: 
    Heat generation per technology/source at NUTS0 level (q)
    Population density per region (rho)
    Total population per region r (p)
    Minimal network infrastructure requirements of t (sigma)
    Available heat network infrastructure potential at r (pi) (derived from population density)
    
output:
    Heat generation per technology/source on NUTS3 level (q_hat)
"""


def sequential_downscaling(
    generation=None, needs=None, pop_density=None, population=None
):

    if u.validate_input_data(generation, pop_density, population):

        _model = generation.model
        _unit = generation.unit
        _year = generation.year

        technologies = generation.variable
        requirements = u.initialization(technologies, needs)
        loc_demand = u.pop_based_downscaling(generation, population)

        _dict_gen = u.iamdf_to_dict(df=generation, keys=["scenario", "variable"])
        _dict_pot = u.iamdf_to_dict(df=pop_density, keys=["region"])


        _res = dict()

        for _sce in generation.scenario:
            _loc_gen = u.sequential_algorithm(
                _dict_gen, loc_demand, requirements, _dict_pot, _sce
            )
            _res = {**_res, **_loc_gen}

        col_names = ["Scenario", "Variable", "Region", "Value"]
        df = u.dict_to_iamdf(_res, col_names)

        df.insert(1, "model", _model[0])
        df.insert(1, "unit", _unit[0])
        df.insert(1, "year", _year[0])

        iamdf = IamDataFrame(df)
        return iamdf

    else:
        return None
