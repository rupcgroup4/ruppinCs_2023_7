import numpy as np
from gym import Env
from gym.spaces import Discrete, Box, Dict


class SpyEnv_v2(Env):

  def __init__(self, state, flights):
    
    self.flights = flights
    

    self.initial_state = state.copy()

    self.state = state.copy()
    
    self.observation_space = Dict({
      "spyPosition": Discrete(len(flights)),
      "agent1Position": Discrete(len(flights)),
      "agent2Position": Discrete(len(flights)),
      "targetPosition": Discrete(len(flights)),
      })
    
    # for i in range(len(flights)):
    #   self.state[str(i)] = flights[i]['destinations']
    #   self.observation_space[str(i)] = Box(low=0, high=len(flights), shape=(len(flights[i]['destinations']),))
    #   self.initial_state[str(i)] = flights[i]['destinations']

    

    self.action_space = Discrete(len(flights))


    self.agents_path = {
      "agnet1Position": [],
      "agent2Position": []
    }

    self.win = 0
    self.lose = 0
    self.ilegal_step = 0
    self.episode_steps = 0

  

  #action = represent index of airpor in array
  def step(self, action):
    self.episode_steps+=1
    reward = 0
    done = False
    info = {}

    #check if action is legal
    legal_flights = self.getPossibleFlightsFromCurrentPosition(self.state["spyPosition"])
    if(action not in legal_flights):
      self.ilegal_step +=1
      reward = -50
      return self.state, reward, True, info

    #Move spy
    self.state["spyPosition"] = action

    #Calculate reward
    if self.isSpyAndAgentInSamePosition(): 
      self.lose +=1
      reward = -50
      done = True
    elif self.state['spyPosition'] == self.state['targetPosition']: 
      self.win +=1
      reward = 100
      shortest_path_legth = len(self.shortest_path(self.initial_state['spyPosition'], self.state['targetPosition'])) - 1
      if(shortest_path_legth == self.episode_steps):
        reward = 150
      done = True
    #
    else:
      # move agents
      self.moveOpponentAgent('agent1Position')
      self.moveOpponentAgent('agent2Position')

      # check if spy lose after agents moved
      if self.isSpyAndAgentInSamePosition(): 
        self.lose +=1
        reward = -50
        done = True

    return self.state, reward, done, info
  
  def isSpyAndAgentInSamePosition(self):
    return self.state['spyPosition'] == self.state['agent1Position'] or self.state['spyPosition'] == self.state['agent2Position']

  #currentPoistion is Tuple (row,col)
  def getPossibleFlightsFromCurrentPosition(self, currentPosition):
    return self.flights[currentPosition]['destinations']
  

  def moveOpponentAgent(self, agentNum):
    agentAirportIndex = self.state[agentNum]

    # actionType = np.random.choice([1, 2], 1, p = [0.9, 0.1])
    
    # if actionType == 1:
    #   airPortIndex = self.getAgentNextAirPortByShortestPath(agentAirportIndex)
    # else:
    #   airPortIndex = self.getAgentNextAirportByRandom(agentAirportIndex)

    airPortIndex = self.getAgentNextAirPortByShortestPath(agentAirportIndex, agentNum)
  
    
    #set agent new state position
    self.state[agentNum] = airPortIndex
    
  
  def getAgentNextAirPortByShortestPath(self, agentAirportIndex, agentNum):
    #calculate shortest path between agent to spy
    spyAirportIndex = self.state['spyPosition']
    path = self.shortest_path(agentAirportIndex, spyAirportIndex)
    if(len(path) == 0):
      if(len(self.agents_path[agentNum]) == 0):
        return self.getAgentNextAirportByRandom(agentAirportIndex)
      return self.agents_path[agentNum][0]
    self.agents_path[agentNum] = path[2:]
    return path[1]

  #get random action based on current position
  def getAgentNextAirportByRandom(self, agentAirportIndex):
    return np.random.choice(self.flights[agentAirportIndex]['destinations']) 



  def shortest_path(self, node1, node2):
    rnd = False
    path_list = [[node1]]
    path_index = 0
    # To keep track of previously visited nodes
    previous_nodes = {node1}
    if node1 == node2:
        return path_list[0]
        
    while path_index < len(path_list):
        current_path = path_list[path_index]
        last_node = current_path[-1]
        next_nodes = self.flights[last_node]['destinations']
        # Search goal node
        if node2 in next_nodes:
            current_path.append(node2)
            return current_path
           
        # Add new paths
        for next_node in next_nodes:
            if not next_node in previous_nodes:
                new_path = current_path[:]
                new_path.append(next_node)
                path_list.append(new_path)
                # To avoid backtracking
                previous_nodes.add(next_node)
        # Continue to next path in list
        path_index += 1
    # No path is found
    return []

  def render(self):
    return
  
  def reset(self):
    self.state = self.initial_state.copy()
    self.episode_steps = 0
    return self.state

  def stats(self):
    return self.win, self.lose, self.ilegal_step

  def reset_stats(self):
    self.win = 0
    self.lose = 0
    self.ilegal_step = 0
    

