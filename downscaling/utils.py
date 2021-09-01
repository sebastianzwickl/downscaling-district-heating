import pyam as py
import logging
import pandas as pd

logger = logging.getLogger(__name__)


def validate_input_data(generation=None, pop_density=None, population=None):

    """
    Parameters
    ----------
    generation : IamDataFrame, required
        Includes the heat generation per technology/source. The default is None.
    pop_density : IamDataFrame, required
        Includes the population density per region. The default is None.
    population : IamDataFrame, optional
        Includes the (total) population per region. The default is None.

    Returns
    -------
    _ret : binary (True/False)
        True if the input data is in appropiate format, else False.

    """

    _string = []
    _ret = True

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
        _ret = False
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
            _ret = False

    return _ret


def initialization(technologies=None, requirements=None):

    """
    Parameters
    ----------
    technologies : list, required
        A list of all heat generation technologies/sources. The default is None.
    requirements : dict, required
        A dictionary including the requirements of heat generation technologies/sources. The default is None.

    Returns
    -------
    requirements : dict
        An updated dictionary including all the requirements of heat generation technologies/sources.

    """

    for _t in technologies:
        if not _t in requirements.keys():
            print(f"No requirements defined for {_t}! (is set to 0)")
            requirements[_t] = 0
    requirements = dict(sorted(requirements.items(), key=lambda x: x[1], reverse=True))
    return requirements


def pop_based_downscaling(generation=None, population=None):

    """
    Parameters
    ----------
    generation : IamDataFrame, required
        Includes the heat generation by technology/source. The default is None.
    population : IamDataFrame, required
        Includes the total population. The default is None.

    Returns
    -------
    demand : dict
        Total heat demand per scenario and region.

    """

    total_generation = dict()
    demand = dict()
    _scenarios = generation.scenario
    for _sce in _scenarios:
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
        Includes the data as an IamDataFrame. The default is none.
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
        Heat generation by technology/source with the following keys: scenario, variable. The default is None.
    demand : dict, required
        Total heat demand per scenario and region. The default is None.
    requirements : dict, required
        Requirements of heat network infrastructure at the local level.
        The default is None.
    potential : dict, required
        Potential of heat network infrastructure at the local level.
        The default is None.
    scenario : string, required
        The default is None.

    Returns
    -------
    _quantity : dict
        Heat generation by source/technology per scenario and region.

    """

    _quantity = dict()
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
            _quantity[scenario, _k_req, _l] = (
                demand[scenario, _l] / _load
            ) * generation[scenario, _k_req]
            demand[scenario, _l] -= _quantity[scenario, _k_req, _l]
    return _quantity


def dict_to_iamdf(dictionary=None, col_name=None):

    """
    Parameters
    ----------
    dictionary : dict, required
        Includes the data that is transformed to an IamDataFrame. The key of the dictionary should include the following IAMC format columns: scenario, variable, region. The default is None.
    columns : dict, required
        Includes additonal information that is used to create a complete IamDataFrame (e.g., model, unit, etc.). The default is None.

    Returns
    -------
    df : IamDataFrame

    """

    df = df = pd.DataFrame(dictionary, index=[0]).T.reset_index()
    df.columns = col_name
    return df
