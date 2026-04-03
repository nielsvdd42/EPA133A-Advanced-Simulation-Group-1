from mesa import Agent
from enum import Enum


# ---------------------------------------------------------------
class Infra(Agent):
    """
    Base class for all infrastructure components

    Attributes
    __________
    vehicle_count : int
        the number of vehicles that are currently in/on (or totally generated/removed by)
        this infrastructure component

    length : float
        the length in meters
    ...

    """

    def __init__(self, unique_id, model, length=0,
                 name='Unknown', road_name='Unknown'):
        super().__init__(unique_id, model)
        self.length = length
        self.name = name
        self.road_name = road_name
        self.vehicle_count = 0

    def step(self):
        pass

    def __str__(self):
        return type(self).__name__ + str(self.unique_id)


# ---------------------------------------------------------------
class Bridge(Infra):
    """
    Creates delay time

    Attributes
    __________
    condition:
        condition of the bridge

    delay_time: int
        the delay (in ticks) caused by this bridge
    ...

    """

    def __init__(self, unique_id, model, length=0,
                 name='Unknown', road_name='Unknown', condition='Unknown', water_dist=5, elevation=None, cyclone_intensity=None):
        super().__init__(unique_id, model, length, name, road_name)

        self.condition = condition
        self.water_dist = water_dist
        self.elevation = elevation
        self.cyclone_intensity = cyclone_intensity
        self.vulnerability_score = 0
        self.state = Bridge.State.HEALED
        self.total_delay = 0


    class State(Enum):
        """
        State enum for setting the state of bridges
        """
        HEALED = 1
        BROKEN = 2


    def get_delay_time(self):
        """
        Calculates the delay time based on random draws from the distributions
        specified in the assignment
        """
        delay_time = 0
        if self.State == Bridge.State.HEALED:
            return delay_time
        else:
            match self.length:
                case n if n < 10:
                    delay_time = self.random.uniform(10,20)
                case n if n < 50:
                    delay_time = self.random.uniform(15,60)
                case n if n < 200:
                    delay_time = self.random.uniform(45, 90)
                case n if n >= 200:
                    delay_time = self.random.triangular(60,240,120)
            self.total_delay += delay_time
            return delay_time

    def calculate_vulnerabilityscore(self):
        """
        Calculates the vulnerability score of a bridge and sets it
        """
        if self.water_dist is None or self.elevation is None or self.cyclone_intensity is None:
            return 0
        water_max = self.model.max_water
        water_min = self.model.min_water
        water_dist = (self.water_dist - water_min) / (water_max - water_min)
        water_dist_score = 1 - water_dist

        elevation_max = self.model.max_elev
        elevation_min = self.model.min_elev
        elevation = (self.elevation - elevation_min) / (elevation_max - elevation_min)
        elevation_score = 1 - elevation

        cyclone_max = self.model.max_cycl
        cyclone_min = self.model.min_cycl
        cyclone_score = (self.cyclone_intensity - cyclone_min) / (cyclone_max - cyclone_min)

        self.vulnerability_score = [water_dist_score, elevation_score, cyclone_score]
        #print(self.vulnerability_score)

    def determine_brokenness(self, weights):
        """
        Calculates whether a bridge is broken or not based on a scenario and individual scores
        """
        if sum(list(weights.values())) != 1:
            print("Weights are wrong")
            return 0
        condition_score = -1
        match self.condition:
            case 'A':
                condition_score = 0
            case 'B':
                condition_score = 0.15
            case 'C':
                condition_score = 0.30
            case 'D':
                condition_score = 0.55
            case _:
                raise Exception("Sorry, wrong bridge condition type")
        geographic_score = weights['w_water'] * self.vulnerability_score[0] + weights['w_elevation'] * self.vulnerability_score[1] + weights['w_cyclone'] * self.vulnerability_score[2]
        probability_broken = 0.5 * geographic_score + 0.5 * condition_score
        if self.random.random() < probability_broken:
            self.state = Bridge.State.BROKEN
            #print(f'Broken with probability {probability_broken}, with condition {condition_score} and {geographic_score}')
            return probability_broken
        else:
            self.state = Bridge.State.HEALED
            #print(f'Healed with probability {probability_broken}, with condition {condition_score} and {geographic_score}')
            return probability_broken


# ---------------------------------------------------------------
class Link(Infra):
    pass


# ---------------------------------------------------------------
class Intersection(Infra):
    pass


# ---------------------------------------------------------------
class Sink(Infra):
    """
    Sink removes vehicles

    Attributes
    __________
    vehicle_removed_toggle: bool
        toggles each time when a vehicle is removed
    ...

    """
    vehicle_removed_toggle = False

    def remove(self, vehicle):
        self.model.schedule.remove(vehicle)
        self.vehicle_removed_toggle = not self.vehicle_removed_toggle
        #print(str(self) + ' REMOVE ' + str(vehicle))


# ---------------------------------------------------------------

class Source(Infra):
    """
    Source generates vehicles

    Class Attributes:
    -----------------
    truck_counter : int
        the number of trucks generated by ALL sources. Used as Truck ID!

    Attributes
    __________
    generation_frequency: int
        the frequency (the number of ticks) by which a truck is generated

    vehicle_generated_flag: bool
        True when a Truck is generated in this tick; False otherwise
    ...

    """

    truck_counter = 0
    generation_frequency = 5
    vehicle_generated_flag = False

    def step(self):
        if self.model.schedule.steps % self.generation_frequency == 0:
            self.generate_truck()
        else:
            self.vehicle_generated_flag = False

    def generate_truck(self):
        """
        Generates a truck, sets its path, increases the global and local counters
        """
        try:
            agent = Vehicle('Truck' + str(Source.truck_counter), self.model, self)
            if agent:
                self.model.schedule.add(agent)
                agent.set_path()
                Source.truck_counter += 1
                self.vehicle_count += 1
                self.vehicle_generated_flag = True
                #print(str(self) + " GENERATE " + str(agent))
        except Exception as e:
            print("Oops!", e.__class__, "occurred.")


# ---------------------------------------------------------------
class SourceSink(Source, Sink):
    """
    Generates and removes trucks
    """
    pass


# ---------------------------------------------------------------
class Vehicle(Agent):
    """

    Attributes
    __________
    speed: float
        speed in meter per minute (m/min)

    step_time: int
        the number of minutes (or seconds) a tick represents
        Used as a base to change unites

    state: Enum (DRIVE | WAIT)
        state of the vehicle

    location: Infra
        reference to the Infra where the vehicle is located

    location_offset: float
        the location offset in meters relative to the starting point of
        the Infra, which has a certain length
        i.e. location_offset < length

    path_ids: Series
        the whole path (origin and destination) where the vehicle shall drive
        It consists the Infras' uniques IDs in a sequential order

    location_index: int
        a pointer to the current Infra in "path_ids" (above)
        i.e. the id of self.location is self.path_ids[self.location_index]

    waiting_time: int
        the time the vehicle needs to wait

    generated_at_step: int
        the timestamp (number of ticks) that the vehicle is generated

    removed_at_step: int
        the timestamp (number of ticks) that the vehicle is removed
    ...

    """

    # 48 km/h translated into meter per min
    speed = 48 * 1000 / 60
    # One tick represents 1 minute
    step_time = 1

    class State(Enum):
        DRIVE = 1
        WAIT = 2

    def __init__(self, unique_id, model, generated_by,
                 location_offset=0, path_ids=None):
        super().__init__(unique_id, model)
        self.generated_by = generated_by
        self.generated_at_step = model.schedule.steps
        self.location = generated_by
        self.location_offset = location_offset
        self.pos = generated_by.pos
        self.path_ids = path_ids
        # default values
        self.state = Vehicle.State.DRIVE
        self.location_index = 0
        self.waiting_time = 0
        self.waited_at = None
        self.removed_at_step = None

    def __str__(self):
        return "Vehicle" + str(self.unique_id) + \
               " +" + str(self.generated_at_step) + " -" + str(self.removed_at_step) + \
               " " + str(self.state) + '(' + str(self.waiting_time) + ') ' + \
               str(self.location) + '(' + str(self.location.vehicle_count) + ') ' + str(self.location_offset)

    def set_path(self):
        """
        Set the origin destination path of the vehicle
        """
        self.path_ids = self.model.get_route(self.generated_by.unique_id)

    def step(self):
        """
        Vehicle waits or drives at each step
        """
        if self.state == Vehicle.State.WAIT:
            self.waiting_time = max(self.waiting_time - 1, 0)
            if self.waiting_time == 0:
                self.waited_at = self.location
                self.state = Vehicle.State.DRIVE

        if self.state == Vehicle.State.DRIVE:
            self.drive()

        """
        To print the vehicle trajectory at each step
        """
        #print(self)

    def drive(self):

        # the distance that vehicle drives in a tick
        # speed is global now: can change to instance object when individual speed is needed
        distance = Vehicle.speed * Vehicle.step_time
        distance_rest = self.location_offset + distance - self.location.length

        if distance_rest > 0:
            # go to the next object
            self.drive_to_next(distance_rest)
        else:
            # remain on the same object
            self.location_offset += distance

    def get_next_id(self):
        if self.location_index + 1 >= len(self.path_ids):
            return None  # reached end
        return self.path_ids[self.location_index + 1]

    def drive_to_next(self, distance):
        """
        vehicle shall move to the next object with the given distance
        """

        self.location_index += 1
        next_id = self.get_next_id()
        if next_id is None:
            # stop moving, or reverse, or loop
            return
        next_infra = self.model.schedule._agents[next_id]  # Access to protected member _agents

        if isinstance(next_infra, Sink):
            # arrive at the sink
            self.arrive_at_next(next_infra, 0)
            self.removed_at_step = self.model.schedule.steps

            driving_time = self.removed_at_step - self.generated_at_step
            self.model.completed_trip_times.append(driving_time)

            self.location.remove(self)
            return
        elif isinstance(next_infra, Bridge):
            if next_infra.state == Bridge.State.BROKEN:
                self.waiting_time = next_infra.get_delay_time()
                print(f"Delay time assigned: {self.waiting_time}")
                print(f"Bridge total_delay: {next_infra.total_delay}")
            if self.waiting_time > 0:
                # arrive at the bridge and wait
                self.arrive_at_next(next_infra, 0)
                self.state = Vehicle.State.WAIT
                return
            # else, continue driving

        if next_infra.length > distance:
            # stay on this object:
            self.arrive_at_next(next_infra, distance)
        else:
            # drive to next object:
            self.drive_to_next(distance - next_infra.length)

    def arrive_at_next(self, next_infra, location_offset):
        """
        Arrive at next_infra with the given location_offset
        """
        self.location.vehicle_count -= 1
        self.location = next_infra
        self.location_offset = location_offset
        self.location.vehicle_count += 1

# EOF -----------------------------------------------------------
