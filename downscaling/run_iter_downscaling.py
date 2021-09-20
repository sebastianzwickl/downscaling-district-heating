from iterative_downscaling import *


def run_iterative_downscaling(country=None, NUTS3=None, scenario=None):

    """

    Parameters
    ----------
    country : String, optional
        NUTS0 country code (e.g., AT for Austria). The default is 'AT'.
    NUTS3 : String, required
        NUTS3 sub-region code. The default is None.

    Returns
    -------
    None.

    """

    european_network = create_initial_network_topology(country=country)
    select_subregion = european_network.loc[
        (european_network["NUTS3_CODE"] == NUTS3)
        & (european_network["scenario"] == scenario)
    ]
    connections = create_connection_lines(
        select_subregion, subregion=NUTS3, scenario=scenario
    )
    generation, lines, indicators = iterative_downscaling(select_subregion, connections)
    string = files_to_results_folder(
        generation=generation,
        lines=lines,
        benchmark=indicators,
        folder=country + "+" + NUTS3,
    )
    plot_final_network_graph(generation, lines, select_subregion, string)
    return


run_iterative_downscaling(country="AT", NUTS3="AT127", scenario="Techno-Friendly")
