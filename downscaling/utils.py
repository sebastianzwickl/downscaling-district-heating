import pyam as py
import logging
import pandas as pd

logger = logging.getLogger(__name__)


def validate_input_data(generation=None, pop_density=None, population=None):

    """

    Parameters
    ----------
    generation : IamDataFrame, required
        Includes the heat generation by technology/source.
        So far, it is necessary to include values of one scenario here.
        This will be updated in further extensions.
        The default is None.
    pop_density : IamDataFrame, required
        Includes the population density of the regions (areas to be downscaled).
        The scenario should be the same as the one of the generation parameter.
        The default is None.
    population : IamDataFrame, required
        Includes the population per region.
        The scenario should be the same as the one of the 'generation' parameter.
        The default is None.

    Returns
    -------
    check : binary (True/False)
        This variable is set to 'True' if all the input data is in the appropiate format.
        Otherwise, it is set to 'False'.

    """

    _string = []
    check = True

    if not isinstance(generation, py.IamDataFrame):
        _string.append("Generation")
    if not isinstance(pop_density, py.IamDataFrame):
        _string.append("Population density")
    if not isinstance(population, py.IamDataFrame):
        _string.append("Population")

    n = len(_string)

    if n != 0:
        msg = (
            "{} input data is not in the IamDataFrame format"
            if n == 1
            else "{} input data are not in the IamDataFrame format"
        )
        logger.warning(msg.format(n, _string))
        check = False
    else:
        logger.info("All input data is in the IamDataFrame format")

        _sce = generation.scenario
        for _s in _sce:
            _pop_den_regions = pop_density.filter(scenario=_s).region
            _pop_regions = population.filter(scenario=_s).region
            if not set(_pop_den_regions) == set(_pop_regions):
                _string.append(_s)

        n = len(_string)
        if n != 0:
            msg = (
                "{} scenario has incomplete input data set"
                if n == 1
                else "Scenarios {} do not have complete input data set"
            )
            logger.warning(msg.format(_string))
            check = False

    return check


def initialization(technologies=None, requirements=None):

    """

    Parameters
    ----------
    technologies : list, required
        A list of heat generation technologies/sources.
        The default is None.
    requirements : dict, required
        Includes the heat network infrastructure requirements of the different
        heat generation technologies. This dictionary should include a specific
        value for each technology/source. If not, the corresponding value is
        set to zero for the technology/source.
        Note that the requirements correspond to the required local population
        density in the current version of the script.
        The default is None.

    Returns
    -------
    full_req : dict
        Includes a complete (full) dictionary related to all technology/source
        specific heat network infrastructure requirements.
        As mentioned, unspecified requirements are set to zero for the
        corresponding technology/source.

    """

    for _t in technologies:
        if not _t in requirements.keys():
            print(f"No requirements defined for {_t}! (is set to 0)")
            requirements[_t] = 0
    full_req = dict(sorted(requirements.items(), key=lambda x: x[1], reverse=True))

    return full_req


def pop_based_downscaling(generation=None, population=None):

    """

    Parameters
    ----------
    generation : IamDataFrame, required
        Includes the heat generation by technology/source.
        So far, it is necessary to include values of one scenario here.
        This will be updated in further extensions.
        The default is None.
    population : IamDataFrame, required
        Includes the population per region.
        The scenario should be the same as the one of the 'generation' parameter.
        The default is None.

    Returns
    -------
    demand : dict
        Includes the population-based downscaled heat demand per region
        (and scenario). Scenario, as part of the dictionary
        key is used for further extensions of the script: for example
        processing multiple scenarios at the same time.

    """

    total_generation = dict()
    demand = dict()
    scenarios = generation.scenario
    for _sce in scenarios:
        total_generation = generation.filter(scenario=_sce).data["value"].sum()
        total_population = population.filter(scenario=_sce).data["value"].sum()
        for _r in population.filter(scenario=_sce).region:
            demand[_sce, _r] = (
                total_generation
                * (
                    population.filter(scenario=_sce, region=_r).data["value"]
                    / total_population
                )[0]
            )

    return demand


def iamdf_to_dict(df=None, keys=None):

    """

    Parameters
    ----------
    df : IamDataFrame, required
        Includes the data in the IAMC format that is tranformed to a dict.
        The default is none.
    keys : list, required
        A list containing the columns of the IamDataFrame used as key.
        The order of elements within the list needs to be same as the columns
        of the IamDataFrame (IAMC format).
        The default is None.

    Returns
    -------
    _dict : dict
        A dictionary with selected keys and corresponding values.

    """

    _dict = dict()
    _pandas_df = df.data
    for index, row in _pandas_df.iterrows():
        _k = []
        if "model" in keys:
            _k.append(row["model"])
        if "scenario" in keys:
            _k.append(row["scenario"])
        if "region" in keys:
            _k.append(row["region"])
        if "variable" in keys:
            _k.append(row["variable"])
        if "unit" in keys:
            _k.append(row["unit"])
        if "year" in keys:
            _k.append(row["year"])

        if len(keys) == 1:
            _dict[_k[0]] = row["value"]
        else:
            _dict[tuple(_k)] = row["value"]

    return _dict


def sequential_algorithm(
    generation=None, demand=None, requirements=None, potential=None, scenario=None
):
    
    """
    
    Parameters
    ----------
    generation : dict, required
        A dictionary including the heat generation by technology/source with 
        scenario and variable as keys. The scenario-related key is already 
        implemented for further extensions of the script. 
        The default is None. 
    demand : dict, required
        A dictionary including the (downscaled) heat demand on the region 
        level with scenario and region as keys. 
        The scenario-related key is already 
        implemented for further extensions of the script. 
        The default is None. 
    requirements : dict, required
        Requirements of heat network infrastructure at the local level. The key
        of the dictionary is the heat generation technology/source. 
        The default is None.
    potential : dict, required
        Potential of heat network infrastructure at the local level. The key
        of the dictionary is the region. 
        The default is None.
    scenario : string, required
        Sets the scenario. This parameter is already considered to help further
        developments of the script related to multiple scenario analyses. 
        The default is None.

    Returns
    -------
    quantity : dict
        The heat generation by technology/source at the local level.
        The key of the dict is a tuple including scenario, variable, 
        and region (in this order).

    """

    quantity = dict()
    for _k_req in requirements.keys():
        _list = []
        _load = 0
        _all_valid_regions = [
            _k for _k, _v in potential.items() if _v >= requirements[_k_req]
        ]

        for _r in _all_valid_regions:
            if demand[scenario, _r] >= 0:
                _list.append(_r)
                _load += demand[scenario, _r]

        for _l in _list:
            quantity[scenario, _k_req, _l] = (
                demand[scenario, _l] / _load
            ) * generation[scenario, _k_req]
            demand[scenario, _l] -= quantity[scenario, _k_req, _l]
    return quantity


def dict_to_df(dictionary=None, col_name=None):

    """

    Parameters
    ----------
    dictionary : dict, required
        Includes a dictionary that is tranformed to the IAMC format and
        IamDataFrame. It is required that the key tuple of the dictionary
        includes the information of the 'scenario', 'variable', and 'region'
        column (in this order).
        The default is None.
    col_name : list, optional
        Includes column names that are used for the IAMC format. If this
        parameter is not passed to the function, the default description,
        as described above in the 'dictionary' description, is used.
        The default is None.

    Returns
    -------
    df : DataFrame

    """

    df = df = pd.DataFrame(dictionary, index=[0]).T.reset_index()

    if col_name == None:
        df.columns = ["Scenario", "Variable", "Region", "Value"]
    else:
        df.columns = col_name

    return df
