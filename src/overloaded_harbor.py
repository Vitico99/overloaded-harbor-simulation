from .pq import PQueue
import src.rdm as rdm

# Constants
PORT = 1
DOCK = 0
EMPTY = 0
FREE = 0

class OverloadedHarbor:

    def __init__(self, N_docks, N_tugboats, L_arrival_time, 
    L_help_time_to_dock, L_help_time_to_port, L_move_time, D_ship_type, D_ship_download, verbose=False) -> None:
        self.N_docks = N_docks
        self.N_tugboats = N_tugboats
        self.L_arrival_time = L_arrival_time
        self.L_help_time_to_dock = L_help_time_to_dock
        self.L_help_time_to_port = L_help_time_to_port
        self.L_move_time = L_move_time
        self.D_ship_type = D_ship_type
        self.D_ship_download = D_ship_download
        self.verbose = verbose

    ############################## Random number generation #############################

    def get_ship_type(self):
        return rdm.discrete_random(self.D_ship_type)

    def get_arrival_time(self):
        return rdm.exp(1/self.L_arrival_time)

    def get_tugboat_move_time(self):
        return rdm.exp(1/self.L_move_time)

    def get_tugboat_help_time(self, arrival=True):
        if arrival:
            return rdm.exp(1/self.L_help_time_to_dock)
        return rdm.exp(1/self.L_help_time_to_port)

    def get_download_time(self, type):
        mean, variance = self.D_ship_download[type]
        return rdm.normal(mean, variance)
         
    ################################### Simulation ##########################################

    def simulate(self, T):
        
        # Time variables
        t = 0 # the current time of the simulation

        # Counting variables
        N_arrived_port = 0
        N_arrived_dock = 0
        N_departed_dock = 0
        N_departed_port = 0

        # State Variables
        port_queue = []
        dock_queue = []
        docks = [0] * self.N_docks
        tugboats = [0] * self.N_tugboats # associates every tugboat with its state
        tugboats_loc = [PORT] * self.N_tugboats # asociates every tugboat with its current location
        ship_type = {}

        # Output variables
        arrived_port = {} # register the time when a ship arrives to the port
        arrived_dock = {} # register the time when a ship arrives to a dock
        departed_dock = {} # register the time when a ship leaves the dock 
        departed_port = {}  # register the time when a ship leaves the port

        # Events
        t_next_arrive = self.get_arrival_time()
        t_arrive_dock = PQueue()
        t_depart_dock = PQueue()
        t_depart_port = PQueue()


        def tug_to_dock(ship, dock, tugboat):
            if self.verbose:
                print(f'Tugboat {tugboat} takes ship {ship} to dock {dock}')

            docks[dock] = ship
            tugboats[tugboat] = ship

            expected_arrival_time = t + self.get_tugboat_help_time()
            if tugboats_loc[tugboat] == DOCK:
                expected_arrival_time += self.get_tugboat_move_time()
            
            t_arrive_dock.insert((expected_arrival_time, tugboat))

        def tug_to_port(ship, tugboat):
            if self.verbose:
                print(f'Tugboat {tugboat} takes ship {ship} to port')
            tugboats[tugboat] = ship
            docks[docks.index(ship)] = FREE
            
            expected_arrival_time = t + self.get_tugboat_help_time(arrival=False)
            if tugboats_loc[tugboat] == PORT:
                expected_arrival_time += self.get_tugboat_move_time()
            
            t_depart_port.insert((expected_arrival_time, tugboat))


        def download_ship_cargo(ship):
            t_depart_dock.insert((t + self.get_download_time(ship_type[ship]), ship)) 


        def reallocate_tugboat(tugboat):
            location = tugboats_loc[tugboat]
            if not port_queue and not dock_queue: # if there are no ships in the docks and in the port
                if location == DOCK:
                    t_depart_port.insert((t + self.get_tugboat_move_time(), tugboat)) # go to port
                else:
                    tugboats[tugboat] = FREE # waith at the port
            
            elif location == DOCK: # the tugboat is at the docks
                if dock_queue: # check if there is a ship ready to leave
                    ship = dock_queue.pop(0)
                    tug_to_port(ship, tugboat)
                elif port_queue and not all(docks): # check the port for ships
                    ship = port_queue.pop(0)
                    dock = docks.index(EMPTY)
                    tug_to_dock(ship, dock, tugboat)
                else:
                    tugboats[tugboat] = FREE # stay in the docks waiting

            elif location == PORT:
                if port_queue and not all(docks):
                    ship = port_queue.pop(0)
                    dock = docks.index(EMPTY)
                    tug_to_dock(ship, dock, tugboat)
                elif dock_queue:
                    ship = dock_queue.pop(0)
                    tug_to_port(ship, tugboat)
                else:
                    tugboats[tugboat] = FREE

        def next_event():
            return min([t_next_arrive, t_arrive_dock.min()[0],
            t_depart_dock.min()[0], t_depart_port.min()[0]])

        event = next_event()

        while event < float('inf'):
            
            # A ship arrives to port
            if event == t_next_arrive:

                t = t_next_arrive

                t_next_arrive += self.get_arrival_time()
                if t_next_arrive > T:
                    t_next_arrive = float('inf')

                N_arrived_port += 1 # Generate and register the arrival
                ship = N_arrived_port 
                ship_type[ship] = self.get_ship_type()
                arrived_port[ship] = t
                if self.verbose:
                    print(f'Ship {ship} arrived to the port')

                
                if port_queue or all(docks) or all(tugboats):
                    port_queue.append(ship)
                    if self.verbose:
                        print(f'Ship {ship} joins the port queue')
                else: 
                    dock = docks.index(EMPTY)
                    tugboat = tugboats.index(FREE)

                    tug_to_dock(ship, dock, tugboat)

            # A ship finished its download and departed from a dock 
            elif event == t_depart_dock.min()[0]:
                t, ship = t_depart_dock.pop()

                N_departed_dock += 1
                departed_dock[ship] = t
                if self.verbose:
                    print(f'Ship {ship} finish its download')


                if dock_queue or all(tugboats):
                    dock_queue.append(ship)
                    if self.verbose:
                        print(f'Ship {ship} joins the dock queue')
                else:
                    tugboat = tugboats.index(FREE)
                    tug_to_port(ship, tugboat)



            # A ship arrives to dock event
            elif event == t_arrive_dock.min()[0]:
                t, tugboat = t_arrive_dock.pop()
                
                ship = tugboats[tugboat]
                
                if ship:
                    if self.verbose:
                        print(f'Ship {ship} arrived to the dock {docks.index(ship)} and start downloading the cargo')
                    N_arrived_dock += 1
                    arrived_dock[ship] = t
                    download_ship_cargo(ship)

                tugboats_loc[tugboat] = DOCK
                reallocate_tugboat(tugboat) 

            elif event == t_depart_port.min()[0]:
                t, tugboat = t_depart_port.pop()

                ship = tugboats[tugboat] 
                if ship:
                    N_departed_port += 1
                    departed_port[ship] = t
                    if self.verbose:
                        print(f'Ship {ship} leaves the port')

                tugboats_loc[tugboat] = PORT
                reallocate_tugboat(tugboat)

            event = next_event()

        return arrived_port, arrived_port, departed_dock, departed_port         