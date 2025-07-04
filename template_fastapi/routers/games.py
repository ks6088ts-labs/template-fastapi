import random

from fastapi import APIRouter

from template_fastapi.opentelemetry import get_meter, get_tracer

tracer = get_tracer(__name__)
meter = get_meter(__name__)

# Add counter for dice rolls
roll_counter = meter.create_counter(
    "dice.rolls",
    description="The number of rolls by roll value",
)

router = APIRouter()


@router.get("/roll_dice", operation_id="roll_dice")
async def roll_dice():
    """
    Simulate rolling a dice and record the roll in the meter.
    """
    with tracer.start_as_current_span("roll_dice"):
        roll = random.randint(1, 6)
        roll_counter.add(1, {"roll.value": str(roll)})
    return roll
