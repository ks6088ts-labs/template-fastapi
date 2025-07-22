import asyncio
import random

from fastapi import APIRouter, HTTPException

from template_fastapi.opentelemetry import get_meter, get_tracer
from template_fastapi.settings.logging import get_logger

logger = get_logger(__name__)
tracer = get_tracer(__name__)
meter = get_meter(__name__)
router = APIRouter()


@tracer.start_as_current_span("flaky_exception")
@router.get("/flaky/exception", operation_id="flaky_exception")
async def flaky_exception():
    """
    A flaky endpoint that always raises an exception.
    """
    logger.warning("Flaky exception endpoint called - simulating error")
    raise HTTPException(
        status_code=500,
        detail="Simulated exception",
    )


@router.get("/flaky/{failure_rate}", operation_id="flaky")
async def flaky(failure_rate: int):
    """
    A flaky endpoint that simulates a failure based on the provided failure rate.

    The failure rate is a percentage (0-100) that determines the likelihood of failure.
    """
    logger.debug(f"Flaky endpoint called with failure rate: {failure_rate}")

    if not (0 <= failure_rate <= 100):
        logger.error(f"Invalid failure rate: {failure_rate}")
        raise HTTPException(
            status_code=400,
            detail="Failure rate must be between 0 and 100",
        )

    random_value = random.randint(0, 100)
    if random_value < failure_rate:
        logger.warning(f"Simulating failure (random: {random_value}, threshold: {failure_rate})")
        raise HTTPException(
            status_code=500,
            detail="Simulated failure",
        )

    logger.info(f"Request succeeded (random: {random_value}, threshold: {failure_rate})")
    return {
        "message": "Request succeeded",
    }


@router.get("/heavy_sync/{sleep_ms}", operation_id="heavy_sync_with_sleep")
async def heavy_sync_with_sleep(sleep_ms: int):
    """
    A heavy synchronous endpoint that sleeps for the specified number of milliseconds.

    This simulates a long-running synchronous operation.
    """
    logger.info(f"Heavy sync endpoint called with sleep time: {sleep_ms}ms")

    if sleep_ms < 0:
        logger.error(f"Invalid sleep time: {sleep_ms}")
        raise HTTPException(
            status_code=400,
            detail="Sleep time must be a non-negative integer",
        )

    with tracer.start_as_current_span("parent"):
        logger.debug(f"Starting sleep for {sleep_ms} milliseconds")
        await asyncio.sleep(sleep_ms / 1000.0)  # Convert milliseconds to seconds
        with tracer.start_as_current_span("child"):
            logger.debug("Child span execution")
    logger.info(f"Completed sleep operation for {sleep_ms}ms")
    return {
        "message": f"Slept for {sleep_ms} milliseconds",
    }


roll_counter = meter.create_counter(
    "dice.rolls",
    description="The number of rolls by roll value",
)


@router.get("/roll_dice", operation_id="roll_dice")
async def roll_dice():
    """
    Simulate rolling a dice and record the roll in the meter.
    """
    with tracer.start_as_current_span("roll_dice"):
        roll = random.randint(1, 6)
        logger.info(f"Dice rolled: {roll}")
        roll_counter.add(1, {"roll.value": str(roll)})
    return roll
