from FileHandler import FileHandler
from VotingRules import VotingRules
from ValueGeneration import ValueGeneration
from Distortion import Distortion

file_handler = FileHandler('00004-00000001.soc')

# Generating Values
value_generation = ValueGeneration(file_handler.votes_dict, file_handler.num_alternatives)
k_list = value_generation.generate_k_instance({'uniform': (2,2), 'gamma': (1,0.5)}, True)
k_list_normalized = value_generation.unit_sum_normalization(k_list)
print(k_list)
print(k_list_normalized)

# Applying Scoring Rules
file_handler.voting_rule_init()
vr = VotingRules(file_handler.votes_dict, file_handler.num_alternatives)
veto = vr.veto_rule()
winner = vr.winner_probability(veto)  # or winner = vr.winner_probability(veto)
print(veto, 'Winner is', winner)

# Calculating Distortion
distortion = Distortion(k_list)
print(distortion.average_distortion(10,winner))
# print(distortion.distortion(winner))


winner2 = vr.winner_determinstic(veto)
print(distortion.distortion(winner2))