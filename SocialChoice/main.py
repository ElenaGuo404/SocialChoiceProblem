from FileHandler import FileHandler
from DeterministicFunctions import DeterministicFunctions
from RandomizedFunctions import RandomizedFunctions

file_handler = FileHandler('00004-00000001.soc')

file_handler.extract_information()

votes_dict = file_handler.create_dict()
# #
# # # Example usage of the created dictionary
print(votes_dict)
#
social_choice = DeterministicFunctions(votes_dict)
randomized = RandomizedFunctions(votes_dict)

veto = social_choice.plurality_rule()
result = social_choice.k_approval_rule(2)

print(veto)
print(result)
#
# borda_result = social_choice.borda_count()
# print(borda_result)
