import simpy
import random
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from rich.logging import RichHandler
import logging

# Setup Rich logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)],
)

logger = logging.getLogger("rich")

RANDOM_SEED = 42
CALL_DURATION = 14  # Average time a call takes in minutes
CALL_INTERVAL = 2  # Average time between calls in minutes
SIM_TIME = 600  # Simulation time in minutes
NUM_OPERATORS = 4

# Data storage for the simulation results
times = []
operators_occupied = []


class CallCenter(object):
    def __init__(self, env, num_operators):
        self.env = env
        self.operator = simpy.PriorityResource(env, num_operators)
        logger.info(f"Call center initialized with {num_operators} operators.")

    def handle_call(self, call, priority):
        logger.info(f"Handling {call} with priority {priority}...")
        yield self.env.timeout(CALL_DURATION)
        logger.info(f"{call} handled in {CALL_DURATION} minutes.")


def call(env, name, cc, priority):
    arrival_time = env.now
    logger.info(f"{name} with priority {priority} arrived at {arrival_time} minutes.")
    with cc.operator.request(priority=priority) as request:
        yield request
        handle_time = env.now
        logger.info(f"{name} started being handled at {handle_time} minutes.")
        yield env.process(cc.handle_call(name, priority))
        leave_time = env.now
        logger.info(f"{name} finished at {leave_time} minutes.")


def setup(env, num_operators):
    call_center = CallCenter(env, num_operators)
    i = 0
    while True:
        priority = random.choice([0, 1, 2])  # 0 = high, 1 = medium, 2 = low
        yield env.timeout(random.randint(CALL_INTERVAL - 2, CALL_INTERVAL + 2))
        env.process(call(env, f"Call {i}", call_center, priority))
        times.append(env.now)
        operators_occupied.append(call_center.operator.count)
        i += 1


def update_plot(frame_number, times, operators_occupied, line):
    line.set_data(times[:frame_number], operators_occupied[:frame_number])
    return (line,)


def run_simulation():
    random.seed(RANDOM_SEED)
    env = simpy.Environment()
    env.process(setup(env, NUM_OPERATORS))
    env.run(until=SIM_TIME)

    fig, ax = plt.subplots()
    (line,) = ax.plot([], [], "r-")
    ax.set_xlim(0, SIM_TIME)
    ax.set_ylim(0, NUM_OPERATORS + 1)
    ax.set_xlabel("Time (minutes)")
    ax.set_ylabel("Operators Occupied")
    ani = animation.FuncAnimation(
        fig,
        update_plot,
        frames=len(times),
        fargs=(times, operators_occupied, line),
        blit=True,
        interval=5000 / SIM_TIME,
        repeat=False,
    )
    plt.show()


run_simulation()
