from FileHandler import FileHandler
from Functions import Functions

file_handler = FileHandler('00004-00000001.soc')
file_handler.extract_information()

votes_dict = file_handler.create_dict()

# Example usage of the created dictionary
print(votes_dict)

social_choice = Functions(votes_dict)
result = social_choice.majority_rule()

borda_result = social_choice.borda_count()
print(borda_result)
