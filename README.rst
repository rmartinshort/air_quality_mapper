====================
air_pollution_mapper
====================


.. image:: https://img.shields.io/pypi/v/air_pollution_mapper.svg
        :target: https://pypi.python.org/pypi/air_pollution_mapper

.. image:: https://img.shields.io/travis/rmartinshort/air_pollution_mapper.svg
        :target: https://travis-ci.com/rmartinshort/air_pollution_mapper

.. image:: https://readthedocs.org/projects/air-pollution-mapper/badge/?version=latest
        :target: https://air-pollution-mapper.readthedocs.io/en/latest/?version=latest
        :alt: Documentation Status




Make use of Google APIs to answer questions about pollutants and generate maps


* Free software: MIT license
* Documentation: https://air-pollution-mapper.readthedocs.io.


Basic usage
--------

Use the google APIs to fetch current or historical pollutant information for a given location

.. code-block:: python

    from air_pollution_mapper.api_caller.utils import load_secrets
    self.secrets = load_secrets()
    self.client = Client(key=self.secrets["GOOGLE_MAPS_API_KEY"])

    # current conditions
    from air_pollution_mapper.api_caller.current_conditions import current_conditions

    location = {"longitude": -122.3, "latitude": 37.8}
    current_condition_resp = current_conditions(self.client, location)

    # historical conditions
    from air_pollution_mapper.api_caller.historical_conditions import historical_conditions

    lag_hours = 24
    historical_condition_resp = historical_conditions(
            self.client, location, lag_time=lag_hours
    )

    # pollution heatmap tile
    from air_pollution_mapper.api_caller.air_quality_heatmap_tile import air_quality_tile

    tile = air_quality_tile(location,zoom=4)



Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
