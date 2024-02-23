from FileHandler import FileHandler
from DeterministicFunctions import DeterministicFunctions
from RandomizedFunctions import RandomizedFunctions
from ValueGeneration import ValueGeneration

file_handler = FileHandler('00004-00000001.soc')
# file_handler.extract_information()
#
# print(file_handler.data)
# print(file_handler.num_alternatives)

# file_handler2 = FileHandler('00004-00000001.soc')
# file_handler2.extract_information2()
# print(file_handler2.data)

# file_handler.generate_complete_file()
# print(file_handler.data)

# file_handler.generate_complete_file()

votes_dict = file_handler.votes_dict
# print(file_handler.data)
# print(votes_dict)

# file_handler.generate_strict_file()
# print(file_handler.data)
# print(votes_dict)
# # print(len(votes_dict))
value_generation = ValueGeneration(votes_dict,3)
# print(value_generation.data_dict)

# print(value_generation.num_alternatives)
# print(value_generation.generate_complete_file(votes_dict))
# print(value_generation.make_data_strict(votes_dict))
value_generation.value_generation("00004-00000001_values.soc","gamma",False)
#
print(value_generation.data_dict)
# print(value_generation.unit_range_normalization())

# # # Example usage of the created dictionary

# #
# social_choice = DeterministicFunctions(votes_dict)
#
# h = social_choice.veto_rule()
# randomized = RandomizedFunctions(h)

# print(value_generation.value_generation2())
# socring_rule = social_choice.scoring_rule([1,1,0])
# result = social_choice.k_approval_rule(2)
#


# print(h)
#
# print(randomized.winner_probability())
# print(randomized.winner_randomized())
# print(result)
#
# borda_result = social_choice.borda_count()
# print(borda_result)
