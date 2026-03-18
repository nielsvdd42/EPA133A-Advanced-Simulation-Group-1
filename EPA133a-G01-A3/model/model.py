from matplotlib import pyplot as plt
from mesa import Model
from mesa.time import BaseScheduler
from mesa.space import ContinuousSpace
from mesa.datacollection import DataCollector
from components import Source, Sink, SourceSink, Bridge, Link, Intersection
import pandas as pd
from collections import defaultdict
import networkx as nx
from pyvis.network import Network

# ---------------------------------------------------------------
def set_lat_lon_bound(lat_min, lat_max, lon_min, lon_max, edge_ratio=0.02):
    """
    Set the HTML continuous space canvas bounding box (for visualization)
    give the min and max latitudes and Longitudes in Decimal Degrees (DD)

    Add white borders at edges (default 2%) of the bounding box
    """

    lat_edge = (lat_max - lat_min) * edge_ratio
    lon_edge = (lon_max - lon_min) * edge_ratio

    x_max = lon_max + lon_edge
    y_max = lat_min - lat_edge
    x_min = lon_min - lon_edge
    y_min = lat_max + lat_edge
    return y_min, y_max, x_min, x_max

def compute_avg_driving_time(model):
    """Calculates the average driving time of completed trips."""
    if len(model.completed_trip_times) == 0:
        return 0.0
    # print(model.completed_trip_times)
    return sum(model.completed_trip_times) / len(model.completed_trip_times)

# ---------------------------------------------------------------
class BangladeshModel(Model):
    """
    The main (top-level) simulation model

    One tick represents one minute; this can be changed
    but the distance calculation need to be adapted accordingly

    Class Attributes:
    -----------------
    step_time: int
        step_time = 1 # 1 step is 1 min

    path_ids_dict: defaultdict
        Key: (origin, destination)
        Value: the shortest path (Infra component IDs) from an origin to a destination

        Only straight paths in the Demo are added into the dict;
        when there is a more complex network layout, the paths need to be managed differently

    sources: list
        all sources in the network

    sinks: list
        all sinks in the network

    """

    step_time = 1

    file_name = '../data/data_intersectionsN1N2.csv'

    def __init__(self, seed=None, x_max=500, y_max=500, x_min=0, y_min=0, scenario={'A': 0.00, 'B': 0.00, 'C':0.00, 'D':0.00}):

        self.schedule = BaseScheduler(self)
        self.running = True
        self.path_ids_dict = defaultdict(lambda: pd.Series())
        self.space = None
        self.sources = []
        self.sinks = []
        self.scenario = scenario
        self.completed_trip_times = []
        self.G = nx.Graph()
        self.generate_model()

        self.datacollector = DataCollector(
            model_reporters={"Average_Driving_Time": compute_avg_driving_time}
        )

    def generate_model(self):
        """
        generate the simulation model according to the csv file component information

        Warning: the labels are the same as the csv column labels
        """

        df = pd.read_csv(self.file_name)

        # a list of names of roads to be generated
        roads = list(df.road.unique())

        df_objects_all = []
        for road in roads:
            # Select all the objects on a particular road in the original order as in the cvs
            df_objects_on_road = df[df['road'] == road]

            if not df_objects_on_road.empty:
                df_objects_all.append(df_objects_on_road)

                """
                Set the path 
                1. get the serie of object IDs on a given road in the cvs in the original order
                2. add the (straight) path to the path_ids_dict
                3. put the path in reversed order and reindex
                4. add the path to the path_ids_dict so that the vehicles can drive backwards too
                """
                path_ids = df_objects_on_road['id']
                path_ids.reset_index(inplace=True, drop=True)
                self.path_ids_dict[path_ids[0], path_ids.iloc[-1]] = path_ids
                self.path_ids_dict[path_ids[0], None] = path_ids
                path_ids = path_ids[::-1]
                path_ids.reset_index(inplace=True, drop=True)
                self.path_ids_dict[path_ids[0], path_ids.iloc[-1]] = path_ids
                self.path_ids_dict[path_ids[0], None] = path_ids

        # put back to df with selected roads so that min and max and be easily calculated
        df = pd.concat(df_objects_all)
        y_min, y_max, x_min, x_max = set_lat_lon_bound(
            df['lat'].min(),
            df['lat'].max(),
            df['lon'].min(),
            df['lon'].max(),
            0.05
        )

        # ContinuousSpace from the Mesa package;
        # not to be confused with the SimpleContinuousModule visualization
        self.space = ContinuousSpace(x_max, y_max, True, x_min, y_min)
        network_nodes = {"bridges": [], "sourcesinks": [], "intersections": [], "links": {}}
        coord_dict = {}
        for df in df_objects_all:
            for _, row in df.iterrows():  # index, row in ...

                # create agents according to model_type
                model_type = row['model_type'].strip()
                agent = None

                name = row['name']
                if pd.isna(name):
                    name = ""
                else:
                    name = name.strip()

                if model_type == 'source':
                    agent = Source(row['id'], self, row['length'], name, row['road'])
                    self.sources.append(agent.unique_id)
                elif model_type == 'sink':
                    agent = Sink(row['id'], self, row['length'], name, row['road'])
                    self.sinks.append(agent.unique_id)
                elif model_type == 'sourcesink':
                    agent = SourceSink(row['id'], self, row['length'], name, row['road'])
                    self.sources.append(agent.unique_id)
                    self.sinks.append(agent.unique_id)
                    network_nodes["sourcesinks"].append((row['id'], row['length'], row['lon'], row['lat']))
                    coord_dict[row['id']] = (row['lon'], row['lat'])
                elif model_type == 'bridge':
                    agent = Bridge(row['id'], self, row['length'], name, row['road'], row['condition'])
                    network_nodes["bridges"].append((row['id'], row['length'],row['lon'], row['lat']))
                    coord_dict[row['id']] = (row['lon'], row['lat'])
                elif model_type == 'link':
                    agent = Link(row['id'], self, row['length'], name, row['road'])
                    network_nodes["links"][row['id']] = row['length']
                elif model_type == 'intersection':
                    if not row['id'] in self.schedule._agents:
                        agent = Intersection(row['id'], self, row['length'], name, row['road'])
                        network_nodes["intersections"].append((row['id'], row['length'], row['lon'], row['lat']))
                        coord_dict[row['id']] = (row['lon'], row['lat'])

                if agent:
                    self.schedule.add(agent)
                    y = row['lat']
                    x = row['lon']
                    self.space.place_agent(agent, (x, y))
                    agent.pos = (x, y)
        self.generate_network(network_nodes)
        pos = {}
        for node, data in self.G.nodes(data=True):
            # print(node, data)
            pos[node] = (data['lon'], data['lat'])
        # print(nx.is_connected(self.G), nx.number_connected_components(self.G))
        # connected_components = nx.connected_components(self.G)
        # compies = [len(c) for c in sorted(nx.connected_components(self.G), key=len, reverse=True)]
        # nx.draw_networkx(self.G, coord_dict, edge_color='lightgrey')
        # plt.xlim(91.7, 91.9)
        # plt.ylim(22.2, 22.5)
        # plt.savefig(f"compies.png", format="png")
        # self.G = nx.relabel_nodes(self.G, str)
        # net = Network(notebook=True, height="750px", width="100%", bgcolor="#222222", font_color="white")

        # 3. Load the networkx graph
        # net.from_nx(self.G)

        # 4. Show/Save the interactive HTML file
        # net.show("my_interactive_graph.html")

    def generate_network(self, network_dict):
        #Add bridges as nodes to network
        bridges = network_dict["bridges"]
        bridges_with_length = [(bridge[0], {'weight': bridge[1], 'type': 'bridge', 'lon': bridge[2], 'lat': bridge[3]}) for bridge in bridges]
        self.G.add_nodes_from(bridges_with_length)

        sourcesinks = network_dict["sourcesinks"]
        sourcesinks_nodes = [(sourcesink[0], {'weight': sourcesink[1], 'type': 'SoSi', 'lon': sourcesink[2], 'lat': sourcesink[3]}) for sourcesink in sourcesinks]
        self.G.add_nodes_from(sourcesinks_nodes)

        intersections = network_dict["intersections"]
        intersections_nodes = [(intersection[0], {'weight': intersection[1], 'type': 'intersection', 'lon': intersection[2], 'lat': intersection[3]}) for intersection in intersections]
        self.G.add_nodes_from(intersections_nodes)

        links = network_dict["links"]

        paths = self.path_ids_dict
        edge_list = []
        for path_key in paths:
            path = paths[path_key]
            for i in range(len(path) - 1):
                if path.iloc[i] in links:
                    edge_list.append((path.iloc[i-1], path.iloc[i+1], links[path.iloc[i]]))
        # print(edge_list)
        self.G.add_weighted_edges_from(edge_list)
        print(self.G.edges(data=True))
        negative_edges = [(u, v, data) for u, v, data in self.G.edges(data=True) if data.get('weight', 0) < 0]

        if negative_edges:
            print(f"Warning: Found {len(negative_edges)} edges with negative weights!")
            # Print the first 5 to see what the weights actually are
            print(negative_edges[:5])
        print(nx.shortest_path(self.G, 101361, 100001, weight='weight'))


    def get_random_route(self, source):
        """
        pick up a random route given an origin
        """
        while True:
            # different source and sink
            sink = self.random.choice(self.sinks)
            if sink is not source:
                break
        return self.path_ids_dict[source, sink]

    def get_route(self, source):
        while True:
            # different source and sink
            sink = self.random.choice(self.sinks)
            if sink is not source:
                break
        if (source, sink) in self.path_ids_dict:
            print("route exists joepiedepoepie")
            return self.path_ids_dict[source, sink]
        else:
            print(sink, source)
            shortest_path =  nx.shortest_path(self.G, source=source, target=sink, weight='weight')
            self.path_ids_dict[source, sink] = shortest_path
            return shortest_path

    def get_straight_route(self, source):
        """
        pick up a straight route given an origin
        """
        return self.path_ids_dict[source, None]

    def step(self):
        """
        Advance the simulation by one step.
        """
        self.schedule.step()
        self.datacollector.collect(self)


# EOF -----------------------------------------------------------
