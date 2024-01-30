from FileHandler import FileHandler
from DeterministicFunctions import DeterministicFunctions
from RandomizedFunctions import RandomizedFunctions

file_handler = FileHandler('00017-00000001.toi')
file_handler.generate_strict_file()
file_handler.generate_complete_file()
votes_dict = file_handler.create_dict()

# #
# # # Example usage of the created dictionary
print(votes_dict)
#
social_choice = DeterministicFunctions(votes_dict)
randomized = RandomizedFunctions(votes_dict)

# socring_rule = social_choice.scoring_rule([1,1,0])
h = social_choice.veto_rule()
h2 = social_choice.veto_rule2()
# result = social_choice.k_approval_rule(2)
#
# print(socring_rule)
# print(veto)
print(file_handler.get_num_alternatives())
print(social_choice.num_candidates)
print(h)
print(h2)
# print(result)
#
# borda_result = social_choice.borda_count()
# print(borda_result)
