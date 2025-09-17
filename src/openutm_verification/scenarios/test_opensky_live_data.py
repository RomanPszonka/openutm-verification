import time
from functools import partial

from loguru import logger

from openutm_verification.core.clients.flight_blender.flight_blender_client import (
    FlightBlenderClient,
)
from openutm_verification.core.clients.opensky.opensky_client import OpenSkyClient
from openutm_verification.core.execution.scenario_runner import scenario_step
from openutm_verification.core.reporting.reporting_models import ScenarioResult, Status
from openutm_verification.scenarios.common import run_scenario_template
from openutm_verification.scenarios.registry import register_scenario


@register_scenario("opensky_live_data")
def test_opensky_live_data(fb_client: FlightBlenderClient, opensky_client: OpenSkyClient, scenario_name: str) -> ScenarioResult:
    """Fetch live flight data from OpenSky and submit to Flight Blender using template.

    The OpenSky client is provided by the caller; this function focuses on orchestration only.
    """

    # Loop control
    iteration_count = 5  # total number of iterations
    wait_time = 3  # seconds to sleep between iterations

    aggregated_steps = []
    overall_status = Status.PASS
    total_duration = 0.0

    for i in range(iteration_count):
        logger.info(f"OpenSky iteration {i + 1}/{iteration_count}")
        steps = [
            partial(opensky_client.fetch_data),
            partial(fb_client.submit_air_traffic),
        ]

        result = run_scenario_template(
            fb_client=fb_client,
            opensky_client=opensky_client,
            scenario_name=f"{scenario_name} (iter {i + 1})",
            steps=steps,
        )

        aggregated_steps.extend(result.steps)
        total_duration += result.duration_seconds
        if result.status == Status.FAIL:
            overall_status = Status.FAIL

        if i < iteration_count - 1:
            logger.info(f"Waiting {wait_time} seconds before next iteration...")
            time.sleep(wait_time)

    return ScenarioResult(
        name=scenario_name,
        status=overall_status,
        duration_seconds=total_duration,
        steps=aggregated_steps,
    )
