import pyam as py
from sequential_downscaling import *
from utils import iamdf_to_dict
from utils import calculate_heat_density

heat = py.IamDataFrame(
    "Data\GeneSys-Mod_Residential_heat_production_IAMC_format.xlsx"
).filter(year=2050)

population_density = py.IamDataFrame("Data\Population_density.xlsx")

_population_area = py.IamDataFrame("Data\Population+Area.xlsx").filter(year=2050)

population = _population_area.filter(variable="Population", year=2050)
area = _population_area.filter(variable="Total area", year=2050)

requirements = iamdf_to_dict(py.IamDataFrame("Data\Requirements.xlsx"), ["variable"])

_scenarios = heat.scenario
_results = None

for _sce in _scenarios:

    _heat_temp = heat.filter(scenario=_sce).convert_unit("PJ", to="TWh")
    _pop_temp = population.rename(scenario={"Baseline": _sce})
    _pop_den_temp = population_density.rename(scenario={"Baseline": _sce})

    if _results == None:
        _results = sequential_downscaling(
            _heat_temp, requirements, _pop_den_temp, _pop_temp
        )
    else:
        _results.append(
            sequential_downscaling(_heat_temp, requirements, _pop_den_temp, _pop_temp),
            inplace=True,
        )

    _network = [key for key, value in requirements.items() if value >= 150]
    for _t in heat.variable:
        if _t in _network:
            _results.rename(variable={_t: "Centralized|" + _t}, inplace=True)
        else:
            _results.rename(variable={_t: "Decentralized|" + _t}, inplace=True)

_results_to_excel = _results.aggregate(
    variable=["Centralized", "Decentralized"], method="sum", append=False
)
_results_to_excel.to_excel(
    "Sequential-downscaling-results_Centralized+Decentralized_Heat_generation.xlsx",
    include_meta=False,
)

_Heat_density = calculate_heat_density(_results_to_excel, area)
_Heat_density.to_excel(
    "Sequential-downscaling-results_Heat_density.xlsx", include_meta=False
)
