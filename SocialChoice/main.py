from FileHandler import FileHandler
from VotingRules import VotingRules
from ValueGeneration import ValueGeneration
from Distortion import Distortion

file_handler = FileHandler('00004-00000001.soc')

# Generating Values
value_generation = ValueGeneration(file_handler.votes_dict, file_handler.num_alternatives)
value_generation.value_generation("00004-00000001_values.soc", "power", True, 2)
value_list = value_generation.unit_sum_normalization()
print(value_list)

# Applying Scoring Rules
file_handler.voting_rule_init()
vr = VotingRules(file_handler.votes_dict, file_handler.num_alternatives)
veto = vr.veto_rule()
winner = vr.winner_probability(veto)  # or winner = vr.winner_probability(veto)
print(veto, 'Winner is', winner)

# Calculating Distortion
distortion = Distortion(value_list)
print(distortion.average_distortion(10,winner))
# print(distortion.distortion(winner))


winner2 = vr.winner_single(veto)
print(distortion.distortion(winner2))